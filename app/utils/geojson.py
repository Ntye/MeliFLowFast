"""
GeoJSON serialization utilities.
"""
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping


def to_geojson_feature(model_instance):
    """
    Convert a single model instance with geometry to a GeoJSON Feature.
    
    Args:
        model_instance: SQLAlchemy model instance with geom attribute
        
    Returns:
        dict: GeoJSON Feature
    """
    if not hasattr(model_instance, 'geom') or model_instance.geom is None:
        return None
    
    # Convert WKB geometry to Shapely geometry
    shape = to_shape(model_instance.geom)
    
    # Create GeoJSON feature
    feature = {
        'type': 'Feature',
        'geometry': mapping(shape),
        'properties': model_instance.to_dict()
    }
    
    # Remove None geometry type to avoid issues
    if feature['geometry'] is None:
        return None
    
    return feature


def to_geojson_collection(model_instances):
    """
    Convert multiple model instances to a GeoJSON FeatureCollection.
    
    Args:
        model_instances: List of SQLAlchemy model instances with geom attribute
        
    Returns:
        dict: GeoJSON FeatureCollection
    """
    features = []
    
    for instance in model_instances:
        feature = to_geojson_feature(instance)
        if feature is not None:
            features.append(feature)
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def to_geojson(model_instance_or_list):
    """
    Convert model instance(s) to GeoJSON.
    
    Args:
        model_instance_or_list: Single model instance or list of instances
        
    Returns:
        dict: GeoJSON Feature or FeatureCollection
    """
    if isinstance(model_instance_or_list, list):
        return to_geojson_collection(model_instance_or_list)
    else:
        return to_geojson_feature(model_instance_or_list)
