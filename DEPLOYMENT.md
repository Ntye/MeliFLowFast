# Deployment Guide for BeeTrack GeoJSON API

This guide covers deploying the BeeTrack Flask API to Railway with PostGIS support.

## Prerequisites

1. Railway account
2. PostgreSQL with PostGIS extension
3. Git repository connected to Railway

## Quick Deploy to Railway

### Step 1: Setup PostgreSQL with PostGIS

1. In Railway, create a new PostgreSQL database
2. Add the PostGIS extension to your database:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

### Step 2: Configure Environment Variables

Set the following environment variables in Railway:

```bash
# Required
DATABASE_URL=<your-railway-postgres-url>

# Optional
FLASK_ENV=production
SECRET_KEY=<generate-a-secure-secret-key>
API_TITLE=BeeTrack GeoJSON API
API_VERSION=1.0.0

# Clustering Configuration
CLUSTERING_EPS=1000
CLUSTERING_MIN_SAMPLES=2

# Optional Features
ENABLE_GEOCODING=false
```

### Step 3: Deploy Application

Railway will automatically:
1. Detect the Flask application
2. Install dependencies from `requirements.txt`
3. Use the `Procfile` to start the Gunicorn server
4. Deploy the application

### Step 4: Initialize Database

After deployment, initialize the database using Railway's CLI or connect via SSH:

```bash
# Using Railway CLI
railway run flask --app app.py init-db

# Seed sample data (optional)
railway run flask --app app.py seed-db
```

## Manual Database Setup

If you need to create the tables manually:

```sql
-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables (simplified - use Flask commands for full schema)
CREATE TABLE ruchers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geom GEOMETRY(GEOMETRY, 4326) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE ruches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rucher_id INTEGER REFERENCES ruchers(id),
    queen_info JSONB,
    geom GEOMETRY(POINT, 4326) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    ruche_id INTEGER NOT NULL REFERENCES ruches(id),
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    weight FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    signal FLOAT,
    raw JSONB
);

CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    ruche_id INTEGER NOT NULL REFERENCES ruches(id),
    rule_type VARCHAR(100) NOT NULL,
    params JSONB,
    notify_in_app BOOLEAN NOT NULL DEFAULT TRUE,
    notify_whatsapp BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_number VARCHAR(50),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES alert_rules(id),
    ruche_id INTEGER NOT NULL REFERENCES ruches(id),
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    payload JSONB,
    sent_whatsapp BOOLEAN NOT NULL DEFAULT FALSE
);
```

## Testing the Deployment

Once deployed, test the endpoints:

```bash
# Health check
curl https://your-app.railway.app/health

# API status
curl https://your-app.railway.app/status

# API documentation
curl https://your-app.railway.app/docs

# Get all hives (will be empty until you add data)
curl https://your-app.railway.app/geo/ruches

# Get all apiaries
curl https://your-app.railway.app/geo/ruchers
```

## Adding Data

You can add data via:

1. **Seed command**: `railway run flask --app app.py seed-db`
2. **Direct database insertion**: Connect to PostgreSQL and insert data
3. **API endpoints**: (To be implemented) POST endpoints for data creation

Example data insertion:

```sql
-- Insert an apiary
INSERT INTO ruchers (name, description, geom)
VALUES (
    'Central Apiary',
    'Main beekeeping location',
    ST_SetSRID(ST_MakePoint(-73.9654, 40.7829), 4326)
);

-- Insert a hive
INSERT INTO ruches (name, rucher_id, queen_info, geom, active)
VALUES (
    'Hive 1',
    1,
    '{"age": 2, "breed": "Italian"}',
    ST_SetSRID(ST_MakePoint(-73.9654, 40.7829), 4326),
    true
);
```

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correctly set
- Check that PostGIS extension is enabled
- Ensure database tables are created

### Performance Optimization
- Add indexes on frequently queried fields:
  ```sql
  CREATE INDEX idx_ruches_geom ON ruches USING GIST (geom);
  CREATE INDEX idx_ruchers_geom ON ruchers USING GIST (geom);
  CREATE INDEX idx_ruches_active ON ruches(active);
  CREATE INDEX idx_ruches_rucher_id ON ruches(rucher_id);
  ```

### Monitoring
- Use Railway's built-in logs and metrics
- Monitor the `/health` endpoint for database connectivity
- Check Gunicorn worker status in logs

## Scaling

To scale the application:

1. **Vertical scaling**: Increase Railway service resources
2. **Horizontal scaling**: Increase Gunicorn workers in `Procfile`:
   ```
   web: gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 8 --timeout 120
   ```
3. **Database optimization**: Add appropriate indexes and connection pooling

## Security Checklist

- ✅ Debug mode disabled in production (controlled by `FLASK_ENV`)
- ✅ Secret key set via environment variable
- ✅ Database credentials stored in environment variables
- ✅ Input validation on all endpoints
- ✅ CORS configured appropriately
- ⚠️ Consider adding rate limiting for production
- ⚠️ Consider adding authentication/authorization if needed

## Support

For issues or questions:
1. Check application logs in Railway dashboard
2. Review this documentation
3. Check the main README.md for API details
