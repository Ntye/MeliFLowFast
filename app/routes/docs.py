"""
API documentation endpoint.
"""
from flask import Blueprint, jsonify, current_app

bp = Blueprint('docs', __name__, url_prefix='/api')


@bp.route('/', methods=['GET'])
@bp.route('/docs', methods=['GET'])
def api_documentation():
    """
    API documentation endpoint.
    
    Returns:
        JSON with API documentation
    """
    docs = {
        'api_title': current_app.config.get('API_TITLE', 'BeeTrack GeoJSON API'),
        'api_version': current_app.config.get('API_VERSION', '1.0.0'),
        'description': 'Flask API microservice for serving GeoJSON data for beekeeping management',
        'endpoints': {
            'health': {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'response': 'JSON with health status'
            },
            'status': {
                'path': '/status',
                'method': 'GET',
                'description': 'API status with configuration details',
                'response': 'JSON with status information'
            },
            'geo_ruches_all': {
                'path': '/geo/ruches',
                'method': 'GET',
                'description': 'Get GeoJSON for all hives',
                'query_parameters': {
                    'active': 'Filter by active status (true/false)',
                    'rucher_id': 'Filter by rucher (apiary) ID',
                    'cluster': 'Enable clustering (true/false)',
                    'radius': 'Filter by radius in meters (requires lat and lon)',
                    'lat': 'Latitude for radius search',
                    'lon': 'Longitude for radius search'
                },
                'response': 'GeoJSON FeatureCollection'
            },
            'geo_ruche_single': {
                'path': '/geo/ruches/<id>',
                'method': 'GET',
                'description': 'Get GeoJSON for a single hive',
                'path_parameters': {
                    'id': 'Ruche (hive) ID'
                },
                'response': 'GeoJSON Feature'
            },
            'geo_ruchers_all': {
                'path': '/geo/ruchers',
                'method': 'GET',
                'description': 'Get GeoJSON for all apiaries',
                'query_parameters': {
                    'radius': 'Filter by radius in meters (requires lat and lon)',
                    'lat': 'Latitude for radius search',
                    'lon': 'Longitude for radius search'
                },
                'response': 'GeoJSON FeatureCollection'
            },
            'geo_rucher_single': {
                'path': '/geo/ruchers/<id>',
                'method': 'GET',
                'description': 'Get GeoJSON for a single apiary',
                'path_parameters': {
                    'id': 'Rucher (apiary) ID'
                },
                'response': 'GeoJSON Feature'
            },
            'documentation': {
                'path': '/ or /docs',
                'method': 'GET',
                'description': 'API documentation (this endpoint)',
                'response': 'JSON with API documentation'
            }
        },
        'features': {
            'geojson_support': 'Full GeoJSON Feature and FeatureCollection support',
            'postgis_integration': 'PostGIS geometry support for spatial data',
            'spatial_queries': 'Radius-based queries and distance calculations',
            'clustering': 'DBSCAN-based spatial clustering',
            'coordinate_validation': 'Automatic coordinate validation and cleaning',
            'reverse_geocoding': 'Optional reverse geocoding support'
        },
        'database_schema': {
            'ruches': 'Hives with PostGIS Point geometry',
            'ruchers': 'Apiaries with PostGIS Point/Polygon geometry',
            'measurements': 'Sensor data from hives',
            'alert_rules': 'Alert configuration for monitoring',
            'alerts': 'Triggered alerts'
        }
    }
    
    return jsonify(docs), 200
