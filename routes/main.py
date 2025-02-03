from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify
from forms import KeyForm, JWTForm
from models import KeyStore, KeyStorePassword, JWTToken
from encryption_utils import save_keys, generate_jwt_token, verify_keystore_password, set_keystore_password, get_encryption_key
from extensions import db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

# Load valid JWT token at startup
def load_valid_jwt():
    valid_token = JWTToken.query.filter(JWTToken.valid_until > datetime.utcnow()).first()
    if valid_token:
        current_app.config['SNOWFLAKE_AUTH_TOKEN'] = valid_token.token
        current_app.config['SNOWFLAKE_API_URL'] = valid_token.api_url
        return valid_token
    else:
        return None

@main_bp.route("/", methods=["GET", "POST"])
def index():
    key_form = KeyForm()
    jwt_form = JWTForm()
    token = None
    valid_from = None
    valid_until = None

    profiles = KeyStore.query.all()
    jwt_form.profile.choices = [(p.id, p.profile_name) for p in profiles]

    selected_profile = None
    decrypted_keys = None

    # Check if keystore password is set
    keystore_password_entry = KeyStorePassword.query.first()
    if not keystore_password_entry:
        flash('Please set the keystore password first.', 'warning')
        return redirect(url_for('main.set_password'))

    # Save or update keys with password verification
    if key_form.validate_on_submit():
        if verify_keystore_password(key_form.password.data):
            save_keys(
                key_form.profile_name.data,
                key_form.snowflake_url.data,
                key_form.username.data,
                key_form.private_key.data,
                key_form.public_key.data,
                key_form.password.data
            )
            flash('Keys saved/updated successfully.', 'success')
            return redirect(url_for('main.index', _anchor='manage-profile-tab'))
        else:
            flash('Incorrect keystore password.', 'danger')
        return redirect(url_for('main.index'))

    # Generate JWT after password verification
    if jwt_form.validate_on_submit():
        if verify_keystore_password(jwt_form.password.data):
            selected_profile = KeyStore.query.get(jwt_form.profile.data)
            if selected_profile:
                current_app.config['SNOWFLAKE_API_URL'] = selected_profile.snowflake_url
                token = generate_jwt_token(jwt_form.access_lifetime.data, selected_profile, jwt_form.password.data)
                current_app.config['SNOWFLAKE_AUTH_TOKEN'] = token

                # Delete existing token before saving new one
                JWTToken.query.delete()
                db.session.commit()

                # Save token to database
                expiry_time = datetime.utcnow() + timedelta(minutes=int(jwt_form.access_lifetime.data))
                new_token = JWTToken(
                    profile_id=selected_profile.id,
                    token=token,
                    api_url=selected_profile.snowflake_url,
                    valid_from=datetime.utcnow(),
                    valid_until=expiry_time
                )
                db.session.add(new_token)
                db.session.commit()

                flash('JWT token generated and saved successfully.', 'success')
        else:
            flash('Incorrect keystore password.', 'danger')

    valid_token = load_valid_jwt()
    if valid_token:
        selected_profile = KeyStore.query.get(valid_token.profile_id)
        token = valid_token.token
        current_app.config['SNOWFLAKE_AUTH_TOKEN'] = valid_token.token
        current_app.config['SNOWFLAKE_API_URL'] = valid_token.api_url
        valid_from = valid_token.valid_from
        valid_until = valid_token.valid_until

    return render_template("index.html", key_form=key_form, jwt_form=jwt_form, token=token, valid_from=valid_from, valid_until=valid_until, profiles=profiles, selected_profile=selected_profile, decrypted_keys=decrypted_keys)

@main_bp.route("/set_password", methods=["GET", "POST"])
def set_password():
    key_form = KeyForm()
    if request.method == "POST":
        if key_form.password.data:
            set_keystore_password(key_form.password.data)
            flash('Keystore password set successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Password is required to set the keystore.', 'danger')

    return render_template("set_password.html", key_form=key_form)

@main_bp.route("/edit/<int:profile_id>", methods=["POST"])
def edit_profile(profile_id):
    profile = KeyStore.query.get_or_404(profile_id)
    
    # Retrieve JSON data from the request
    data = request.json
    password = data.get('password')
    private_key = data.get('private_key')
    public_key = data.get('public_key')

    if verify_keystore_password(password):
        try:
            # Encrypt the new keys before saving
            fernet = get_encryption_key(password)
            profile.encrypted_private_key = fernet.encrypt(private_key.encode()).decode()
            profile.encrypted_public_key = fernet.encrypt(public_key.encode()).decode()
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Profile updated successfully.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error saving profile: {str(e)}'})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect keystore password. Cannot edit profile.'})

@main_bp.route("/delete/<int:profile_id>", methods=["POST"])
def delete_profile(profile_id):
    profile = KeyStore.query.get_or_404(profile_id)

    if verify_keystore_password(request.json.get('password')):
        db.session.delete(profile)
        db.session.commit()
        flash('Profile deleted successfully.', 'success')
    else:
        flash('Incorrect keystore password. Profile deletion failed.', 'danger')

    return redirect(url_for('main.index', _anchor='manage-profile-tab'))

@main_bp.route("/get_profile", methods=["POST"])
def get_profile():
    profile_id = request.json.get('profile_id')
    password = request.json.get('password')

    selected_profile = KeyStore.query.get(profile_id)
    if selected_profile and verify_keystore_password(password):
        fernet = get_encryption_key(password)
        try:
            decrypted_keys = {
                'profile_name': selected_profile.profile_name,
                'snowflake_url': selected_profile.snowflake_url,
                'username': selected_profile.username,
                'private_key': fernet.decrypt(selected_profile.encrypted_private_key.encode()).decode(),
                'public_key': fernet.decrypt(selected_profile.encrypted_public_key.encode()).decode()
            }
            return jsonify({'status': 'success', 'data': decrypted_keys})
        except Exception:
            return jsonify({'status': 'error', 'message': 'Failed to decrypt keys. Please check the keystore password.'})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect password or profile not found.'})

