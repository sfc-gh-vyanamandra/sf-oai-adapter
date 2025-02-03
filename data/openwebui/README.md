# OpenWebUI Data Directory

This directory (`data/openwebui/`) is used to store database files for the **OpenWebUI** service. The data stored here ensures persistent storage across container restarts.

## Directory Structure
```
data/
└── openwebui/
    └── [Database Files]
```

### Key Points:
- **Location in Host:** `./data/openwebui`
- **Location in Container:** `/app/backend/data`
- **Purpose:** Stores all necessary data and database files required by the OpenWebUI service.

## Persistence
The directory is mounted in the Docker Compose file to ensure that data remains available even after stopping or restarting the container:

```yaml
volumes:
  - ./data/openwebui:/app/backend/data
```

## Managing Data
To inspect or modify the database files within the container:

1. **Access the OpenWebUI container:**
   ```bash
   docker exec -it openwebui bash
   ```

2. **Navigate to the data directory inside the container:**
   ```bash
   cd /app/backend/data
   ```

3. **Inspect the database (if using SQLite):**
   ```bash
   sqlite3 [database_file].db
   ```

## Resetting Admin Password
If you need to reset the admin password for OpenWebUI, follow these steps:

1. **Generate a new password hash:**
   ```bash
   htpasswd -bnBC 10 "" your-new-password | tr -d ':\n'
   ```
   Replace `your-new-password` with your desired password. This will output a hashed password.

2. **Update the password in the database:**
   ```bash
   sqlite3 webui.db "UPDATE auth SET password='HASH' WHERE email='admin@example.com';"
   ```
   Replace `HASH` with the hashed password generated from the previous step.

For more details, refer to the [OpenWebUI Password Reset Documentation](https://docs.openwebui.com/troubleshooting/password-reset/).

## Backup & Restore
To back up your OpenWebUI data, simply copy the contents of the `data/openwebui/` directory to a secure location:

```bash
cp -r ./data/openwebui ./backup/openwebui_backup
```

To restore, copy the backed-up data back into the `data/openwebui/` directory before starting the container.

```bash
cp -r ./backup/openwebui_backup ./data/openwebui
```

## License
This setup follows the licensing terms of the OpenWebUI project. Refer to the OpenWebUI [LICENSE](https://github.com/open-webui/open-webui) for more details.

