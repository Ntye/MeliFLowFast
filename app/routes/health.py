"""
Health check and status endpoints.
"""
from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone
from sqlalchemy import text
from app import db
from app.models import Ruche, Rucher, Measurement, Alert


bp = Blueprint('health', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON with health status
    """
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
        db_message = 'Database connection successful'
    except Exception as e:
        db_status = 'unhealthy'
        db_message = f'Database connection failed: {str(e)}'
    
    health_status = {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'api_version': current_app.config.get('API_VERSION', '1.0.0'),
        'checks': {
            'database': {
                'status': db_status,
                'message': db_message
            }
        }
    }
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return jsonify(health_status), status_code


@bp.route('/status', methods=['GET'])
def status():
    """
    API status endpoint with additional information.
    
    Returns:
        JSON with API status and configuration
    """
    try:
        # Get PostGIS version
        result = db.session.execute(text('SELECT PostGIS_Version()'))
        postgis_version = result.scalar()
    except Exception:
        postgis_version = 'Unknown'
    
    try:
        # Get PostgreSQL version
        result = db.session.execute(text('SELECT version()'))
        pg_version = result.scalar()
    except Exception:
        pg_version = 'Unknown'

    try:
        statistics = {
            'ruches': Ruche.query.count(),
            'ruchers': Rucher.query.count(),
            'measurements': Measurement.query.count(),
            'alerts': Alert.query.count()
        }
    except Exception:
        statistics = 'Could not retrieve statistics'
    
    status_info = {
        'api_title': current_app.config.get('API_TITLE', 'BeeTrack GeoJSON API'),
        'api_version': current_app.config.get('API_VERSION', '1.0.0'),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'database': {
            'postgis_version': postgis_version,
            'postgresql_version': pg_version
        },
        'statistics': statistics,
        'features': {
            'geocoding_enabled': current_app.config.get('ENABLE_GEOCODING', False),
            'clustering_enabled': True,
            'spatial_queries': True
        }
    }
    
    return jsonify(status_info), 200
