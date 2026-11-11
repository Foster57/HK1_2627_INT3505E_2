# Database Migrations

This folder stores Alembic / Flask-Migrate database migration scripts.

To initialize or run migrations with Flask-Migrate:
```bash
# Initialize migrations repository (if not already done)
flask db init

# Generate migration from models
flask db migrate -m "Initial models"

# Apply migration to database
flask db upgrade
```

