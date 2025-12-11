"""
Tests for utility functions.
"""
from app.utils.spatial import validate_coordinates, clean_coordinates, cluster_points


def test_validate_coordinates():
    """Test coordinate validation."""
    # Valid coordinates
    assert validate_coordinates(0, 0) is True
    assert validate_coordinates(-73.9654, 40.7829) is True
    assert validate_coordinates(180, 90) is True
    assert validate_coordinates(-180, -90) is True
    
    # Invalid coordinates
    assert validate_coordinates(181, 0) is False
    assert validate_coordinates(0, 91) is False
    assert validate_coordinates(-181, 0) is False
    assert validate_coordinates(0, -91) is False


def test_clean_coordinates():
    """Test coordinate cleaning."""
    # Valid coordinates
    result = clean_coordinates(-73.9654, 40.7829)
    assert result is not None
    assert result == (-73.9654, 40.7829)
    
    # Invalid coordinates
    assert clean_coordinates(181, 0) is None
    assert clean_coordinates(0, 91) is None
    
    # Invalid types
    assert clean_coordinates('invalid', 'invalid') is None


def test_cluster_points():
    """Test spatial clustering."""
    # Test with no points
    result = cluster_points([])
    assert result['n_clusters'] == 0
    
    # Test with single point
    points = [(0, 0)]
    result = cluster_points(points, min_samples=1)
    assert len(result['labels']) == 1
    
    # Test with multiple points
    points = [
        (-73.9654, 40.7829),
        (-73.9644, 40.7839),
        (-73.9969, 40.7061)
    ]
    result = cluster_points(points, eps=1000, min_samples=2)
    assert 'labels' in result
    assert 'n_clusters' in result
    assert len(result['labels']) == len(points)
