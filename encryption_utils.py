from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import jwt
import base64
import hashlib
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import KeyStore, KeyStorePassword
from extensions import db
from flask import current_app


def get_encryption_key(password):
    salt = b'\x12\x34\x56\x78\x90\xab\xcd\xef'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))


def set_keystore_password(password):
    encrypted_password = generate_password_hash(password)
    existing_password_entry = KeyStorePassword.query.first()

    if existing_password_entry:
        existing_password_entry.encrypted_password = encrypted_password
    else:
        new_password_entry = KeyStorePassword(encrypted_password=encrypted_password)
        db.session.add(new_password_entry)
    db.session.commit()


def verify_keystore_password(provided_password):
    password_entry = KeyStorePassword.query.first()
    if password_entry:
        return check_password_hash(password_entry.encrypted_password, provided_password)
    return False


def save_keys(profile_name, snowflake_url, username, private_key, public_key, password):
    if not verify_keystore_password(password):
        raise ValueError("Invalid keystore password.")

    fernet = get_encryption_key(password)
    encrypted_private_key = fernet.encrypt(private_key.encode()).decode()
    encrypted_public_key = fernet.encrypt(public_key.encode()).decode()

    existing_entry = KeyStore.query.filter_by(profile_name=profile_name).first()
    if existing_entry:
        existing_entry.snowflake_url = snowflake_url
        existing_entry.username = username
        existing_entry.encrypted_private_key = encrypted_private_key
        existing_entry.encrypted_public_key = encrypted_public_key
    else:
        key_entry = KeyStore(
            profile_name=profile_name,
            snowflake_url=snowflake_url,
            username=username,
            encrypted_private_key=encrypted_private_key,
            encrypted_public_key=encrypted_public_key
        )
        db.session.add(key_entry)
    db.session.commit()


def load_keys(password):
    if not verify_keystore_password(password):
        return None

    key_entries = KeyStore.query.all()
    fernet = get_encryption_key(password)
    keys = []

    for entry in key_entries:
        try:
            private_key = fernet.decrypt(entry.encrypted_private_key.encode()).decode()
            public_key = fernet.decrypt(entry.encrypted_public_key.encode()).decode()
            keys.append({
                "profile_name": entry.profile_name,
                "snowflake_url": entry.snowflake_url,
                "username": entry.username,
                "private_key": private_key,
                "public_key": public_key
            })
        except Exception:
            continue

    return keys


def generate_sha256_fingerprint(public_key):
    public_key_bytes = public_key.encode("utf-8")
    public_key_pem = serialization.load_pem_public_key(
        public_key_bytes, backend=default_backend()
    )
    pub_key_der = public_key_pem.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sha256_hash = hashlib.sha256(pub_key_der).digest()
    fingerprint = base64.urlsafe_b64encode(sha256_hash).decode()
    return f"SHA256:{fingerprint}"


def generate_jwt_token(access_lifetime, selected_profile, password):
    if not verify_keystore_password(password):
        return "Error: Invalid keystore password."

    fernet = get_encryption_key(password)
    try:
        private_key = fernet.decrypt(selected_profile.encrypted_private_key.encode()).decode()
        public_key = fernet.decrypt(selected_profile.encrypted_public_key.encode()).decode()
    except Exception:
        return "Error: Unable to decrypt keys."

    public_key_fingerprint = generate_sha256_fingerprint(public_key)
    payload = {
        "iss": f"{selected_profile.username}.{public_key_fingerprint}",
        "sub": selected_profile.username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=int(access_lifetime)),
    }

    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token
    except Exception as e:
        return f"Error: {str(e)}"

