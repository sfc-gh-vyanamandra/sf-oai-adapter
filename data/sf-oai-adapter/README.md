# sf-oai-adapter

A Flask-based application that bridges OpenAI-like requests with Snowflake's Large Language Model (LLM) services. It offers both a web interface and API endpoints for managing encrypted Snowflake profiles and generating JWT tokens for secure access.

## Database Information

### `keys.db`
- **Location:** `/app/instance/keys.db`
- **Description:** This SQLite database stores encrypted Snowflake profile details, user passwords, and JWT tokens. It is automatically created when the application starts if it doesn't already exist.

### Database Tables
1. **KeyStore**: Stores Snowflake profile information with encrypted keys.
2. **KeyStorePassword**: Stores hashed passwords for profile access.
3. **JWTToken**: Manages JWT tokens for secure API authentication.

### Persistent Storage
To persist `keys.db` on the host machine, the following volume is mounted in the Docker Compose file:
```yaml
volumes:
  - ./data/sf-oai-adapter:/app/instance
```

This ensures that the database is saved in `./data/sf-oai-adapter` on the host, making it persistent across container restarts.

### Initializing the Database
The application automatically initializes the database and creates the necessary tables on startup using the following code in `app.py`:
```python
with app.app_context():
    db.create_all()
```

If the database or tables are missing, the application will recreate them when it starts.

## Running the Application

### Using Docker Compose
To run the application and ensure the database is created:
```bash
docker-compose up --build
```

### Accessing the Database
If you need to inspect or modify the database inside the running container:
```bash
docker exec -it sf-oai-adapter bash
sqlite3 /app/instance/keys.db
```

Use standard SQLite commands to query the database:
```sql
.tables  -- List all tables
SELECT * FROM KeyStore;  -- View data in KeyStore
```

### Resetting the application

- Stop the running application and delete the keys.db file.
  
    ```bash
    rm -f /app/instance/keys.db
    ```

- Removing the keys.db file should reset the **Snowflake Cortex REST API Adapter** application.

- During the startup of the application, the db and the tables are all **created automatically** due to the below code in app.py
  
    ```python
    with app.app_context():
        db.create_all()
    ```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
