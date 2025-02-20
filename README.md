# sf-oai-adapter

A Flask-based application that bridges OpenAI-like requests with Snowflake's Large Language Model (LLM) services. It offers both a web interface and API endpoints for managing encrypted Snowflake profiles. This application generates JWT tokens that are used to securely access the Snowflake Cortex REST API.


❗	** *This project is not an officially supported product of Snowflake. Use at your own risk.* **


## Table of Contents
- [Features](#features)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [API Usage](#api-usage)
- [Database Models](#database-models)
- [Encryption](#encryption)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features
- Manage Snowflake profiles with encrypted key storage.
- Generate and manage JWT tokens for secure API access.
- Transform OpenAI-API-like requests into Snowflake-Cortex-REST-API compatible formats.
- Web interface for user-friendly key management.
- API endpoints for programmatic interactions.

## Quickstart
1. **Clone the repository:**
   ```bash
   git clone https://github.com/sfc-gh-vyanamandra/sf-oai-adapter.git
   ```
   
2. **Ensure docker/docker-compose are installed:**
   ```
    % docker -v
     Docker version 26.1.1, build 4cf5afaefa
    % docker-compose -v
     Docker Compose version 2.27.0
   ```
   
3. **Start-up services:**

   This will start up **OpenWebUI** and **sf-oai-adapter** services.
   
   ```bash
   docker-compose up -d
   ```
   
4. **Set up the KeyStore password first:**

   * Use the browser to navigate to http://0.0.0.0:8081. If there is no keystore password already set up in the system, it will prompt you to enter one.
   
       ** Remember this password as it will be used for Inserting/Updating/Deleting KeyProfiles from the KeyStore.
   
       ** This password is also used to generate a valid JWT token to be used while talking to Snowflake Cortex API.
     
   * Add a KeyProfile using the **Add a Key Profile** tab of http://0.0.0.0:8081
     
   * Generate a JWT Authtoken based on a KeyProfile.
     
           
5. **Open OpenWebUI and use the Snowflake hosted LLM models for completions:**

   * This has been setup to use the local adapter url for talking to Snowflake.
  
   * Using a valid JWT token generated above, requests are then sent to the Cortex API URL as the user corresponding to the KeyProfile.


      **Note:**
     
        * Any requests made for `snowflake[<llm-name>]` will be sent to the Snowflake Cortex Rest API.*

        * Use an incognito window if the regular browser does not open the page
     
          * Although this [issue](https://github.com/open-webui/open-webui/issues/9249) is closed, I am suspecting it is still valid.  I could get past this only by using an incognito window for the first time.
          


## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/sfc-gh-vyanamandra/sf-oai-adapter.git
   cd sf-oai-adapter
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

## Configuration
Edit the `config.py` file or set environment variables to configure the application.

- **SNOWFLAKE_LLM_MODELS**: Dictionary of Snowflake LLM models with their configurations.

Example:
```python
class Config:
    SNOWFLAKE_LLM_MODELS = {
        "snowflake[claude-3-5-sonnet]": {"model": "claude-3-5-sonnet", "max_tokens": 18000},
        "snowflake[deepseek-r1]": {"model": "deepseek-r1", "max_tokens": 128000}
    }
```

## Usage

### Web Interface
1. **Access the web interface:** Navigate to `http://0.0.0.0:8081` in your browser.
2. **Set Password:** Secure your Key Profiles with a password (like a *KeyStore* password.)
     **Note**: 
     * This screen appears only the first time when there is no keystore password already.
     * If you lose the keystore password, you have to (factory) reset the system by deleting the `instance/keys.db` file.
   
3. **Manage Profiles:**
   - **Add Profile:** Input Snowflake URL, username, and upload public/private keys.
     
      **Note**: Add key-based authentication for the user in Snowflake first.

     *Reference*: https://docs.snowflake.com/en/user-guide/key-pair-auth#configuring-key-pair-authentication to add 
     
       - **Snowflake URL**: https://\<accountid\>.snowflakecomputing.com
       - **Username**: All CAPS - \<ACCOUNTID\>.\<USERNAME\> (e.g., **UMW02095.SUNEV**)
       - **Public key**: Starts with: "**-----BEGIN PUBLIC KEY-----**" and ends with "**-----END PUBLIC KEY-----**"
       - **Private key**: Unencrypted (for now.) It starts with: "**-----BEGIN PRIVATE KEY-----**" and ends with "**-----END PRIVATE KEY-----**"

   - **Edit/Delete Profile:** Modify existing profile details.

4. **Generate JWT Tokens:** Use the provided interface to generate tokens for API authentication.
   
     **Note**: *Once a new token is generated, all the requests that are made to the application are then sent over to the username's snowflake_url corresponding to the active token.*

### API Usage

- **List Available Models:**

  **Endpoint:** `/v1/models`
  **Method:** `GET`

  **Response Example:**
  ```json
  {
    "data": [
      {"id": "snowflake[claude-3-5-sonnet]", "object": "model", "max_tokens": 18000},
      {"id": "snowflake[deepseek-r1]", "object": "model", "max_tokens": 128000}
    ]
  }
  ```

## Database Models

1. **KeyStore**: Stores encrypted Snowflake profile information.
   ```python
   class KeyStore(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       profile_name = db.Column(db.Text, nullable=False, unique=True)
       snowflake_url = db.Column(db.Text, nullable=False)
       username = db.Column(db.Text, nullable=False, unique=True)
       encrypted_private_key = db.Column(db.Text, nullable=False)
       encrypted_public_key = db.Column(db.Text, nullable=False)
   ```

2. **KeyStorePassword**: Manages passwords for encrypted profiles.
   ```python
   class KeyStorePassword(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       keystore_id = db.Column(db.Integer, db.ForeignKey('key_store.id'))
       hashed_password = db.Column(db.String(128), nullable=False)
   ```

## Encryption

- **Key Encryption**: Uses `Fernet` encryption for storing keys securely.
- **Password Hashing**: Utilizes `werkzeug.security` for secure password management.
- **JWT Tokens**: Generated using `PyJWT` for secure API access.

Example function to encrypt a key:
```python
def get_encryption_key(password):
    salt = b'\x00' * 16  # Example salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))
```

## Troubleshooting

1. **Model Snapshot Path Error:**
   
   **Error Message:**
   ```
   ERROR [open_webui.retrieval.utils] Cannot determine model snapshot path: Consistency check failed: file should be of size 23026053 but has size 46052106 (model_qint8_avx512.onnx).
   ```

   **Solutions:**
   - **Corrupted Model File:** Delete `model_qint8_avx512.onnx` in `./data/openwebui` and restart the container to trigger a fresh download.
     ```bash
     rm ./data/openwebui/model_qint8_avx512.onnx
     docker-compose down
     docker-compose up --force-recreate
     ```

   - **Volume Conflict:** Temporarily remove the volume mapping in `docker-compose.yml` to check if the issue persists:
     ```yaml
     volumes:
       # - ./data/openwebui:/app/backend/data  # Comment this line temporarily
     ```

   - **Image Update:** Ensure you're using the latest image by pulling updates:
     ```bash
     docker pull ghcr.io/open-webui/open-webui:main
     docker-compose up --force-recreate
     ```

   - **File Size Verification:** Check the file size manually to ensure it matches the expected size (23,026,053 bytes):
     ```bash
     ls -l ./data/openwebui/model_qint8_avx512.onnx
     ```

2. **Cannot Connect to Snowflake:**

   **Possible Causes:**
   - Invalid Snowflake URL or credentials.
   - Incorrect public/private key format.
   
   **Solutions:**
   - Verify that the Snowflake URL and username are correct.
   - Ensure the public and private keys are correctly formatted and unencrypted.
   - Check network connectivity and firewall settings.

3. **JWT Token Errors:**

   **Possible Causes:**
   - Expired or invalid token.
   - Mismatch between token and Snowflake profile.

   **Solutions:**
   - Regenerate the JWT token using the web interface.
   - Ensure the active profile matches the credentials used for token generation.

4. **Database Errors:**

   **Possible Causes:**
   - Corrupted `keys.db` file.
   - Missing database migrations.

   **Solutions:**
   - Delete the `instance/keys.db` file to reset the database.
     ```bash
     rm ./data/sf-oai-adapter/keys.db
     docker-compose down
     docker-compose up --force-recreate
     ```
   - Ensure all migrations are applied if using Flask-Migrate.

5. **HTTP Codes:**

   **500 Internal Server Error:**
   ```xml
   <!doctype html>
   <html lang=en>
   <title>500 Internal Server Error</title>
   <h1>Internal Server Error</h1>
   <p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>
   ```
   **Possible Causes:**
   - Invalid or expired JWT token
   - Connect to Snowflake is not possible. E.g., did not login to my VPN.

   **Solutions:**
   - Generate a new JWT token
   - Connect to a VPN if that is mandatory for your snowflake connection from the given machine.
     
## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

