"""
GeoJSON API endpoints for ruches and ruchers.
"""
import json
import numpy as np
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func
from geoalchemy2 import functions as geo_func
from geoalchemy2.functions import ST_AsGeoJSON, ST_DWithin, ST_Distance
from app import db
from app.models import Ruche, Rucher
from app.utils.geojson import to_geojson
from app.utils.spatial import find_within_radius, cluster_points, get_point_coordinates

bp = Blueprint('geo', __name__, url_prefix='/api/geo')

# ========================================
# HELPER FUNCTIONS from flask_postgis_api.py
# ========================================
def validate_coordinates(lat, lon):
    """Validate latitude and longitude"""
    try:
        lat = float(lat)
        lon = float(lon)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, (lat, lon)
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"


def get_clusters(n_clusters=3):
    """Get K-means clusters of hives"""
    ruches = Ruche.query. all()
    
    if len(ruches) < n_clusters:
        return None, f"Need at least {n_clusters} hives to cluster"
    
    # Extract coordinates
    coords = []
    for ruche in ruches:
        geom_json = db.session.query(ST_AsGeoJSON(ruche.geom)).scalar()
        if geom_json:
            geom = json.loads(geom_json)
            coords.append(geom['coordinates'])
    
    coords = np.array(coords)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)
    
    # Build response
    clusters = {}
    for idx, (ruche, label) in enumerate(zip(ruches, labels)):
        label = int(label)
        if label not in clusters:
            clusters[label] = {
                'cluster_id': label,
                'center': [float(kmeans.cluster_centers_[label][0]), 
                          float(kmeans. cluster_centers_[label][1])],
                'features': []
            }
        
        geom_json = db.session. query(ST_AsGeoJSON(ruche.geom)).scalar()
        if geom_json:
            geom = json. loads(geom_json)
            clusters[label]['features'].append({
                'id': ruche.id,
                'name': ruche.name,
                'coordinates': geom['coordinates']
            })
    
    return list(clusters.values()), None


@bp.route('/ruches', methods=['GET'])
def get_all_ruches():
    """
    Get GeoJSON for all hives (ruches).
    
    Query Parameters:
        - active: Filter by active status (true/false)
        - rucher_id: Filter by rucher (apiary) ID
        - cluster: Enable clustering (true/false)
        - radius: Filter by radius in meters (requires lat and lon)
        - lat: Latitude for radius search
        - lon: Longitude for radius search
    
    Returns:
        GeoJSON FeatureCollection
    """
    try:
        # Start with base query
        query = Ruche.query
        
        # Apply filters
        active = request.args.get('active')
        if active is not None:
            query = query.filter(Ruche.active == (active.lower() == 'true'))
        
        rucher_id = request.args.get('rucher_id')
        if rucher_id:
            try:
                query = query.filter(Ruche.rucher_id == int(rucher_id))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid rucher_id parameter'}), 400
        
        # Radius search
        radius = request.args.get('radius')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if radius and lat and lon:
            try:
                center_point = f'POINT({float(lon)} {float(lat)})'
                ruches = find_within_radius(Ruche, center_point, float(radius))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid radius parameters'}), 400
        else:
            ruches = query.all()
        
        # Generate GeoJSON
        geojson = to_geojson(ruches)
        
        # Optional clustering
        if request.args.get('cluster', '').lower() == 'true':
            points = []
            for ruche in ruches:
                coords = get_point_coordinates(ruche.geom)
                if coords:
                    points.append(coords)
            
            if points:
                eps = current_app.config.get('CLUSTERING_EPS', 1000)
                min_samples = current_app.config.get('CLUSTERING_MIN_SAMPLES', 2)
                cluster_info = cluster_points(points, eps=eps, min_samples=min_samples)
                geojson['clustering'] = cluster_info
        
        return jsonify(geojson), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching ruches: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/ruches/<int:ruche_id>', methods=['GET'])
def get_ruche(ruche_id):
    """
    Get GeoJSON for a single hive (ruche).
    
    Args:
        ruche_id: ID of the ruche
    
    Returns:
        GeoJSON Feature
    """
    try:
        ruche = db.session.get(Ruche, ruche_id)
        
        if not ruche:
            return jsonify({'error': 'Ruche not found'}), 404
        
        geojson = to_geojson(ruche)
        
        if geojson is None:
            return jsonify({'error': 'Invalid geometry'}), 500
        
        return jsonify(geojson), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching ruche {ruche_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/ruchers', methods=['GET'])
def get_all_ruchers():
    """
    Get GeoJSON for all apiaries (ruchers).
    
    Query Parameters:
        - radius: Filter by radius in meters (requires lat and lon)
        - lat: Latitude for radius search
        - lon: Longitude for radius search
    
    Returns:
        GeoJSON FeatureCollection
    """
    try:
        # Radius search
        radius = request.args.get('radius')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if radius and lat and lon:
            try:
                center_point = f'POINT({float(lon)} {float(lat)})'
                ruchers = find_within_radius(Rucher, center_point, float(radius))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid radius parameters'}), 400
        else:
            ruchers = Rucher.query.all()
        
        geojson = to_geojson(ruchers)
        
        return jsonify(geojson), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching ruchers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/ruchers/<int:rucher_id>', methods=['GET'])
def get_rucher(rucher_id):
    """
    Get GeoJSON for a single apiary (rucher).
    
    Args:
        rucher_id: ID of the rucher
    
    Returns:
        GeoJSON Feature
    """
    try:
        rucher = db.session.get(Rucher, rucher_id)
        
        if not rucher:
            return jsonify({'error': 'Rucher not found'}), 404
        
        geojson = to_geojson(rucher)
        
        if geojson is None:
            return jsonify({'error': 'Invalid geometry'}), 500
        
        return jsonify(geojson), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching rucher {rucher_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ========================================
# NEW ROUTES from flask_postgis_api.py
# ========================================

@bp.route('/ruches/nearby', methods=['GET'])
def nearby_ruches():
    """Get hives within radius (in meters)"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', default=1000, type=int)
        
        if lat is None or lon is None: 
            return jsonify({'error':  'lat and lon parameters required'}), 400
        
        valid, result = validate_coordinates(lat, lon)
        if not valid: 
            return jsonify({'error': result}), 400
        
        # Query ruches within radius
        point = f'SRID=4326;POINT({lon} {lat})'
        nearby_query = db.session.query(
            Ruche,
            ST_Distance(Ruche.geom, point, use_geography=True).label('distance')
        ).filter(
            ST_DWithin(Ruche.geom, point, radius, use_geography=True)
        )
        
        nearby = nearby_query.all()

        features = []
        for ruche, distance in nearby:
            feature = to_geojson(ruche)
            if feature:
                feature['properties']['distance_meters'] = float(distance)
                features.append(feature)

        return jsonify({
            'type':  'FeatureCollection',
            'query': {'lat': lat, 'lon': lon, 'radius_meters': radius},
            'features': features
        }), 200
    except Exception as e: 
        current_app.logger.error(f"Error in nearby query: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/clusters', methods=['GET'])
def clusters():
    """Get clustered hives using K-means"""
    try: 
        n_clusters = request. args.get('n_clusters', default=3, type=int)
        
        if n_clusters < 1:
            return jsonify({'error':  'n_clusters must be >= 1'}), 400
        
        cluster_data, error = get_clusters(n_clusters)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'clusters': cluster_data,
            'total_clusters': len(cluster_data),
            'n_clusters_requested': n_clusters
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in clustering: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/distance', methods=['GET'])
def distance():
    """Calculate distance between two points"""
    try:
        lat1 = request.args.get('lat1', type=float)
        lon1 = request.args. get('lon1', type=float)
        lat2 = request.args.get('lat2', type=float)
        lon2 = request.args.get('lon2', type=float)
        
        if None in [lat1, lon1, lat2, lon2]:
            return jsonify({'error': 'lat1, lon1, lat2, lon2 parameters required'}), 400
        
        valid1, _ = validate_coordinates(lat1, lon1)
        valid2, _ = validate_coordinates(lat2, lon2)
        
        if not valid1 or not valid2:
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        point1 = f'SRID=4326;POINT({lon1} {lat1})'
        point2 = f'SRID=4326;POINT({lon2} {lat2})'
        
        distance_m = db.session.query(
            ST_Distance(point1, point2, use_geography=True)
        ).scalar()
        
        return jsonify({
            'distance_meters': float(distance_m),
            'distance_km': float(distance_m) / 1000,
            'coordinates': {
                'point1': [lon1, lat1],
                'point2': [lon2, lat2]
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error calculating distance: {str(e)}")
        return jsonify({'error':  str(e)}), 500


@bp.route('/reverse-geocode', methods=['GET'])
def reverse_geocode():
    """Reverse geocode coordinates to address"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None: 
            return jsonify({'error': 'lat and lon parameters required'}), 400
        
        valid, _ = validate_coordinates(lat, lon)
        if not valid: 
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        try:
            geolocator = Nominatim(user_agent="beetrackapi")
            location = geolocator.reverse(f"{lat}, {lon}")
            
            return jsonify({
                'lat': lat,
                'lon': lon,
                'address': location.address,
                'country': location.address.split(',')[-1].strip()
            }), 200
        except: 
            # Fallback if reverse geocoding fails
            return jsonify({
                'lat': lat,
                'lon': lon,
                'address': 'Address not found',
                'country':  'Unknown'
            }), 200
    except Exception as e:
        current_app.logger.error(f"Error in reverse geocode: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/validate-coords', methods=['POST'])
def validate_coords():
    """Validate coordinates"""
    try:
        data = request.get_json()
        
        if not data: 
            return jsonify({'error': 'JSON body required'}), 400
        
        lat = data.get('lat')
        lon = data.get('lon')
        
        valid, result = validate_coordinates(lat, lon)
        
        if valid:
            return jsonify({
                'valid': True,
                'lat':  result[0],
                'lon': result[1],
                'message': 'Coordinates are valid'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': result
            }), 400
    except Exception as e: 
        current_app.logger.error(f"Error validating coords: {str(e)}")
        return jsonify({'error': str(e)}), 500