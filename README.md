"# BeeTrack GeoJSON API

Flask API microservice that connects to a PostGIS database and serves GeoJSON data for beekeeping management system.

## Features

### Core Functionality
- **GeoJSON Endpoints**: Serve spatial data for hives (ruches) and apiaries (ruchers)
- **PostGIS Integration**: Full PostGIS geometry support with SRID 4326
- **Spatial Operations**: 
  - Radius-based queries
  - Distance calculations
  - DBSCAN clustering
  - Coordinate validation
- **Optional Features**: Reverse geocoding with Geopy
- **Health & Documentation**: Health check and API documentation endpoints

### Database Schema
The API supports the following PostGIS-enabled tables:
- **ruches**: Hives with Point geometry
- **ruchers**: Apiaries with Point/Polygon geometry
- **measurements**: Sensor data from hives
- **alert_rules**: Alert configuration
- **alerts**: Triggered alerts

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS extension
- Railway account (for deployment) or local PostgreSQL

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd MeliFlowFlaskTest
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Initialize the database:
```bash
flask --app app.py init-db
```

6. (Optional) Seed with sample data:
```bash
flask --app app.py seed-db
```

## Configuration

Set the following environment variables (or edit `.env`):

```bash
# Required
DATABASE_URL=postgresql://user:password@host:port/database

# Optional
FLASK_ENV=development
SECRET_KEY=your-secret-key
CLUSTERING_EPS=1000  # Clustering distance in meters
CLUSTERING_MIN_SAMPLES=2
ENABLE_GEOCODING=false
```

## Usage

### Development Server
```bash
flask --app app.py run
# or
python app.py
```

### Production Server (Gunicorn)
```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

### Railway Deployment
The application is configured for Railway deployment with the included `Procfile`.

1. Connect your GitHub repository to Railway
2. Set the `DATABASE_URL` environment variable (Railway PostgreSQL addon)
3. Deploy automatically on push

## API Endpoints

### GeoJSON Endpoints

#### Get All Hives
```bash
GET /geo/ruches
```
Query parameters:
- `active`: Filter by active status (true/false)
- `rucher_id`: Filter by apiary ID
- `cluster`: Enable clustering (true/false)
- `radius`: Radius in meters (requires lat and lon)
- `lat`: Latitude for radius search
- `lon`: Longitude for radius search

Response: GeoJSON FeatureCollection

#### Get Single Hive
```bash
GET /geo/ruches/<id>
```
Response: GeoJSON Feature

#### Get All Apiaries
```bash
GET /geo/ruchers
```
Query parameters:
- `radius`: Radius in meters (requires lat and lon)
- `lat`: Latitude for radius search
- `lon`: Longitude for radius search

Response: GeoJSON FeatureCollection

#### Get Single Apiary
```bash
GET /geo/ruchers/<id>
```
Response: GeoJSON Feature

### Supporting Endpoints

#### Health Check
```bash
GET /health
```
Response: JSON with health status and database connectivity

#### Status
```bash
GET /status
```
Response: JSON with API version, PostGIS version, and features

#### Documentation
```bash
GET /docs
```
Response: JSON with complete API documentation

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
MeliFlowFlaskTest/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── ruche.py         # Hive model
│   │   ├── rucher.py        # Apiary model
│   │   ├── measurement.py   # Measurement model
│   │   ├── alert_rule.py    # Alert rule model
│   │   └── alert.py         # Alert model
│   ├── routes/              # API routes
│   │   ├── geo.py           # GeoJSON endpoints
│   │   ├── health.py        # Health check endpoints
│   │   └── docs.py          # Documentation endpoint
│   └── utils/               # Utility functions
│       ├── geojson.py       # GeoJSON serialization
│       ├── spatial.py       # Spatial operations
│       └── geocoding.py     # Reverse geocoding
├── tests/                   # Test suite
├── config.py                # Configuration management
├── app.py                   # Main application entry point
├── wsgi.py                  # WSGI entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment config
└── README.md                # This file
```

## Technology Stack

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM
- **GeoAlchemy2**: PostGIS support
- **Psycopg2**: PostgreSQL driver
- **Shapely**: Geometric operations
- **Geopy**: Geocoding (optional)
- **Scikit-learn**: Clustering
- **Gunicorn**: Production server

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request." 
"# MeliFLowFast" 
