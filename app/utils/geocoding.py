"""
Geocoding utilities for reverse geocoding coordinates to addresses.
"""
from typing import Optional, Dict
from flask import current_app


def reverse_geocode(latitude: float, longitude: float) -> Optional[Dict]:
    """
    Perform reverse geocoding to get address from coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        dict: Address information or None if geocoding is disabled/fails
    """
    # Check if geocoding is enabled
    if not current_app.config.get('ENABLE_GEOCODING', False):
        return None
    
    try:
        from geopy.geocoders import Nominatim
        
        user_agent = current_app.config.get('GEOCODING_USER_AGENT', 'BeeTrack-API')
        geolocator = Nominatim(user_agent=user_agent)
        
        # Perform reverse geocoding
        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        
        if location:
            return {
                'address': location.address,
                'raw': location.raw
            }
        
        return None
        
    except Exception as e:
        current_app.logger.warning(f"Reverse geocoding failed: {str(e)}")
        return None
