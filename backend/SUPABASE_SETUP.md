# Supabase Setup and Configuration

This document provides comprehensive setup instructions for the Supabase Python client in the Claude Code Observatory project.

## Overview

The project uses Supabase as its backend database and real-time service. The setup follows the official [supabase-py documentation](https://github.com/supabase/supabase-py) patterns and includes proper error handling, configuration management, and testing support.

## Dependencies

### Production Dependencies (requirements.txt)
```
supabase==2.3.4        # Main Supabase Python client
python-dotenv==1.0.1    # Environment variable loading
```

### Development Dependencies (requirements-dev.txt)
```
pytest-asyncio==0.23.5  # Async testing support
aiofiles==24.1.0        # Async file operations
asyncpg==0.29.0         # Direct PostgreSQL async driver
psycopg2-binary==2.9.9  # PostgreSQL adapter
```

## Environment Configuration

### Environment Variables

Copy `backend/env.template` to `backend/.env` and configure:

```bash
# Required - Get from your Supabase project dashboard
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here

# Optional - For server-side operations requiring elevated privileges
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key-here

# Optional - Direct database connection
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
```

### Getting Your Keys

1. Go to [app.supabase.com](https://app.supabase.com/)
2. Select your project
3. Navigate to **Settings** > **API**
4. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY` (optional, for admin operations)

## Usage Patterns

### Basic Client Initialization

```python
import os
from supabase import create_client, Client

# Recommended pattern from official documentation
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
```

### Using the Project's Client Manager

```python
from app.database.supabase_client import get_supabase_client

# Get configured client
client = get_supabase_client()

# Use client for database operations
data = client.table("conversations").select("*").execute()
```

### Database Operations

```python
# Select data
data = client.table("countries").select("*").eq("country", "IL").execute()

# Insert data
data = client.table("countries").insert({"name": "Germany"}).execute()

# Update data
data = client.table("countries").update({
    "country": "Indonesia", 
    "capital_city": "Jakarta"
}).eq("id", 1).execute()

# Upsert data
country = {"country": "United Kingdom", "capital_city": "London"}
data = client.table("countries").upsert(country).execute()

# Delete data
data = client.table("countries").delete().eq("id", 1).execute()
```

### Authentication

```python
# Sign up new user
user = client.auth.sign_up({
    "email": "user@example.com", 
    "password": "password123"
})

# Sign in existing user
user = client.auth.sign_in_with_password({
    "email": "user@example.com", 
    "password": "password123"
})

# Important: Always sign out when done
client.auth.sign_out()
```

### Storage Operations

```python
bucket_name = "photos"

# Upload file
data = client.storage.from_(bucket_name).upload("/user1/profile.png", file_data)

# Download file
data = client.storage.from_(bucket_name).download("photo1.png")

# List files
data = client.storage.from_(bucket_name).list()

# Remove files
data = client.storage.from_(bucket_name).remove(["old_photo.png"])

# Move files
data = client.storage.from_(bucket_name).move("old_path.png", "new_path.png")
```

## Testing Setup

### Running Tests

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run Supabase configuration tests
pytest tests/test_supabase_config.py -v

# Run all tests
pytest -v
```

### Mocking in Tests

```python
from unittest.mock import patch, MagicMock
from supabase import Client

def test_with_mock_client():
    with patch('app.database.supabase_client.create_client') as mock_create:
        mock_client = MagicMock(spec=Client)
        mock_client.table.return_value.select.return_value.execute.return_value = {"data": []}
        mock_create.return_value = mock_client
        
        # Your test code here
        from app.database.supabase_client import get_supabase_client
        client = get_supabase_client()
        result = client.table("test").select("*").execute()
        
        assert result["data"] == []
```

## Security Best Practices

### Environment Variables
- **Never commit `.env` files** to version control
- Use `python-dotenv` to load environment variables in development
- In production, set environment variables directly in your deployment platform

### API Keys
- **anon key**: Safe to expose in frontend code, has Row Level Security (RLS) restrictions
- **service_role key**: Keep secret! Only use server-side, bypasses RLS

### Database Security
- Always enable Row Level Security (RLS) on your tables
- Use the anon key for client-side operations
- Only use service_role key for admin operations that require bypassing RLS

## Performance Considerations

### Connection Pooling
The Supabase client manages connections automatically, but for high-throughput applications:

```python
# Consider using asyncpg directly for better performance
import asyncpg

async def direct_db_connection():
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL"))
    # Perform operations
    await conn.close()
```

### Batching Operations
```python
# Batch inserts for better performance
data = [
    {"name": "Country1", "code": "C1"},
    {"name": "Country2", "code": "C2"},
    # ... more records
]
result = client.table("countries").insert(data).execute()
```

## Troubleshooting

### Common Issues

1. **Invalid API Key Error**
   - Verify your API key format (should be a JWT token starting with `eyJ`)
   - Check that you're using the correct key for your environment

2. **Connection Timeouts**
   - Check your network connection
   - Verify the Supabase URL is correct
   - Consider increasing timeout settings

3. **Permission Denied**
   - Verify Row Level Security policies
   - Check that your user has the correct permissions
   - Ensure you're using the right API key (anon vs service_role)

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## Project Integration

### File Structure
```
backend/
├── app/
│   └── database/
│       └── supabase_client.py    # Client manager and configuration
├── tests/
│   └── test_supabase_config.py   # Configuration tests
├── env.template                  # Environment template
├── requirements.txt              # Production dependencies
└── requirements-dev.txt          # Development dependencies
```

### Next Steps

1. **Set up your Supabase project** at [app.supabase.com](https://app.supabase.com/)
2. **Configure environment variables** using the template
3. **Run tests** to verify setup: `pytest tests/test_supabase_config.py -v`
4. **Create database tables** using Supabase migrations
5. **Implement your application logic** using the client manager

## Additional Resources

- [Supabase Python Documentation](https://github.com/supabase/supabase-py)
- [Supabase Dashboard](https://app.supabase.com/)
- [Supabase SQL Editor](https://app.supabase.com/project/YOUR_PROJECT/sql)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)