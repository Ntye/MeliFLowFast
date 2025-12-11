"""
Main Flask application entry point.
"""
from datetime import datetime, timezone
from app import create_app, db

# Create Flask application
app = create_app()


@app.cli.command()
def init_db():
    """Initialize the database with PostGIS extension."""
    with app.app_context():
        # Enable PostGIS extension
        from sqlalchemy import text
        try:
            db.session.execute(text('CREATE EXTENSION IF NOT EXISTS postgis'))
            db.session.commit()
            print("PostGIS extension enabled")
        except Exception as e:
            print(f"Warning: Could not enable PostGIS extension: {e}")
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully")


@app.cli.command()
def seed_db():
    """Seed the database with sample data for testing."""
    with app.app_context():
        from app.models import Ruche, Rucher
        from geoalchemy2.elements import WKTElement
        from datetime import datetime
        
        # Check if data already exists
        if Rucher.query.count() > 0:
            print("Database already contains data. Skipping seeding.")
            return
        
        # Create sample ruchers (apiaries)
        rucher1 = Rucher(
            name="Apiary Central Park",
            description="Main apiary in Central Park",
            geom=WKTElement('POINT(-73.9654 40.7829)', srid=4326),
            created_at=datetime.now(timezone.utc)
        )
        
        rucher2 = Rucher(
            name="Apiary Brooklyn Bridge",
            description="Apiary near Brooklyn Bridge",
            geom=WKTElement('POINT(-73.9969 40.7061)', srid=4326),
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(rucher1)
        db.session.add(rucher2)
        db.session.commit()
        
        # Create sample ruches (hives)
        ruche1 = Ruche(
            name="Hive Alpha",
            rucher_id=rucher1.id,
            queen_info={"age": 2, "breed": "Italian"},
            geom=WKTElement('POINT(-73.9654 40.7829)', srid=4326),
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        ruche2 = Ruche(
            name="Hive Beta",
            rucher_id=rucher1.id,
            queen_info={"age": 1, "breed": "Carniolan"},
            geom=WKTElement('POINT(-73.9644 40.7839)', srid=4326),
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        ruche3 = Ruche(
            name="Hive Gamma",
            rucher_id=rucher2.id,
            queen_info={"age": 3, "breed": "Buckfast"},
            geom=WKTElement('POINT(-73.9969 40.7061)', srid=4326),
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(ruche1)
        db.session.add(ruche2)
        db.session.add(ruche3)
        db.session.commit()
        
        print(f"Database seeded with {Rucher.query.count()} ruchers and {Ruche.query.count()} ruches")


if __name__ == '__main__':
    # Debug mode is controlled by FLASK_ENV environment variable
    # Only enable debug mode in development environment
    import os
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
