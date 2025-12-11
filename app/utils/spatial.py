"""
Spatial operations and utilities for geographic data.
"""
from typing import List, Tuple, Optional
import numpy as np
from shapely.geometry import Point
from sqlalchemy import func
from sklearn.cluster import DBSCAN
from app import db


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        longitude: Longitude value
        latitude: Latitude value
        
    Returns:
        bool: True if coordinates are valid
    """
    return -180 <= longitude <= 180 and -90 <= latitude <= 90


def clean_coordinates(longitude: float, latitude: float) -> Optional[Tuple[float, float]]:
    """
    Clean and validate coordinates.
    
    Args:
        longitude: Longitude value
        latitude: Latitude value
        
    Returns:
        tuple: Cleaned (longitude, latitude) or None if invalid
    """
    try:
        lon = float(longitude)
        lat = float(latitude)
        
        if validate_coordinates(lon, lat):
            return (lon, lat)
        return None
    except (ValueError, TypeError):
        return None


def calculate_distance(point1_geom, point2_geom) -> float:
    """
    Calculate distance between two PostGIS geometries in meters.
    
    Args:
        point1_geom: First PostGIS geometry
        point2_geom: Second PostGIS geometry
        
    Returns:
        float: Distance in meters
    """
    # Use PostGIS ST_Distance with geography for accurate results
    distance = db.session.query(
        func.ST_Distance(
            func.ST_Transform(point1_geom, 4326),
            func.ST_Transform(point2_geom, 4326),
            True  # Use spheroid for accurate distance
        )
    ).scalar()
    
    return float(distance) if distance else 0.0


def find_within_radius(model_class, center_point, radius_meters: float):
    """
    Find all instances of a model within a radius of a center point.
    
    Args:
        model_class: SQLAlchemy model class with geom attribute
        center_point: Center point as WKT string or Point object
        radius_meters: Radius in meters
        
    Returns:
        list: Query results within radius
    """
    # Create a point from center if it's a string
    if isinstance(center_point, str):
        center_geom = func.ST_GeomFromText(center_point, 4326)
    else:
        center_geom = center_point
    
    # Query using ST_DWithin with geography
    results = model_class.query.filter(
        func.ST_DWithin(
            func.ST_Transform(model_class.geom, 4326),
            func.ST_Transform(center_geom, 4326),
            radius_meters,
            True  # Use spheroid
        )
    ).all()
    
    return results


def cluster_points(points: List[Tuple[float, float]], eps: float = 1000, min_samples: int = 2):
    """
    Cluster geographic points using DBSCAN algorithm.
    
    Args:
        points: List of (longitude, latitude) tuples
        eps: Maximum distance between samples in meters (default 1000m)
        min_samples: Minimum samples in a cluster (default 2)
        
    Returns:
        dict: Dictionary with cluster labels and cluster information
    """
    if not points or len(points) < min_samples:
        return {
            'labels': [-1] * len(points),
            'n_clusters': 0,
            'clusters': {}
        }
    
    # Convert to numpy array
    coords = np.array(points)
    
    # Convert eps from meters to approximate degrees
    # At equator: 1 degree ≈ 111km, so eps_degrees = eps_meters / 111000
    eps_degrees = eps / 111000.0
    
    # Perform DBSCAN clustering
    clustering = DBSCAN(eps=eps_degrees, min_samples=min_samples).fit(coords)
    
    labels = clustering.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    
    # Group points by cluster
    clusters = {}
    for i, label in enumerate(labels):
        if label == -1:  # Noise point
            continue
        
        if label not in clusters:
            clusters[label] = []
        
        clusters[label].append({
            'index': i,
            'coordinates': points[i]
        })
    
    return {
        'labels': labels.tolist(),
        'n_clusters': n_clusters,
        'clusters': clusters
    }


def get_point_coordinates(geom) -> Optional[Tuple[float, float]]:
    """
    Extract coordinates from a PostGIS geometry.
    
    Args:
        geom: PostGIS geometry
        
    Returns:
        tuple: (longitude, latitude) or None
    """
    try:
        from geoalchemy2.shape import to_shape
        shape = to_shape(geom)
        if shape.geom_type == 'Point':
            return (shape.x, shape.y)
        return None
    except Exception:
        return None
