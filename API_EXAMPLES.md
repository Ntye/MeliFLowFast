# BeeTrack API Usage Examples

This document provides practical examples for using the BeeTrack GeoJSON API.

## Base URL

```
http://localhost:5000  # Development
https://your-app.railway.app  # Production
```

## Health & Status Endpoints

### Health Check
Check API and database health:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-11T07:00:00.000000+00:00",
  "api_version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    }
  }
}
```

### Status Information
Get API version and features:

```bash
curl http://localhost:5000/status
```

### API Documentation
Get complete API documentation:

```bash
curl http://localhost:5000/docs
```

## GeoJSON Endpoints

### Get All Hives (Ruches)

Basic request:
```bash
curl http://localhost:5000/geo/ruches
```

Filter by active status:
```bash
curl "http://localhost:5000/geo/ruches?active=true"
```

Filter by apiary:
```bash
curl "http://localhost:5000/geo/ruches?rucher_id=1"
```

Enable clustering:
```bash
curl "http://localhost:5000/geo/ruches?cluster=true"
```

Find hives within radius (1000m from Central Park):
```bash
curl "http://localhost:5000/geo/ruches?lat=40.7829&lon=-73.9654&radius=1000"
```

Combined filters:
```bash
curl "http://localhost:5000/geo/ruches?active=true&rucher_id=1&cluster=true"
```

Response (GeoJSON FeatureCollection):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9654, 40.7829]
      },
      "properties": {
        "id": 1,
        "name": "Hive Alpha",
        "rucher_id": 1,
        "queen_info": {"age": 2, "breed": "Italian"},
        "created_at": "2025-12-11T07:00:00.000000+00:00",
        "active": true
      }
    }
  ]
}
```

### Get Single Hive

```bash
curl http://localhost:5000/geo/ruches/1
```

Response (GeoJSON Feature):
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-73.9654, 40.7829]
  },
  "properties": {
    "id": 1,
    "name": "Hive Alpha",
    "rucher_id": 1,
    "queen_info": {"age": 2, "breed": "Italian"},
    "created_at": "2025-12-11T07:00:00.000000+00:00",
    "active": true
  }
}
```

### Get All Apiaries (Ruchers)

Basic request:
```bash
curl http://localhost:5000/geo/ruchers
```

Find apiaries within radius:
```bash
curl "http://localhost:5000/geo/ruchers?lat=40.7829&lon=-73.9654&radius=5000"
```

Response (GeoJSON FeatureCollection):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9654, 40.7829]
      },
      "properties": {
        "id": 1,
        "name": "Apiary Central Park",
        "description": "Main apiary in Central Park",
        "created_at": "2025-12-11T07:00:00.000000+00:00"
      }
    }
  ]
}
```

### Get Single Apiary

```bash
curl http://localhost:5000/geo/ruchers/1
```

## Using with JavaScript/Frontend

### Fetch API

```javascript
// Get all hives
fetch('http://localhost:5000/geo/ruches')
  .then(response => response.json())
  .then(data => {
    console.log('GeoJSON data:', data);
    // Use with Leaflet, Mapbox, etc.
  });

// Get hives with clustering
fetch('http://localhost:5000/geo/ruches?cluster=true')
  .then(response => response.json())
  .then(data => {
    console.log('Hives:', data.features);
    console.log('Clusters:', data.clustering);
  });

// Get hives within radius
const lat = 40.7829;
const lon = -73.9654;
const radius = 1000; // meters

fetch(`http://localhost:5000/geo/ruches?lat=${lat}&lon=${lon}&radius=${radius}`)
  .then(response => response.json())
  .then(data => {
    console.log('Nearby hives:', data.features);
  });
```

### Leaflet Integration

```javascript
// Create a map
const map = L.map('map').setView([40.7829, -73.9654], 13);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Load and display hives
fetch('http://localhost:5000/geo/ruches')
  .then(response => response.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      onEachFeature: (feature, layer) => {
        const props = feature.properties;
        layer.bindPopup(`
          <strong>${props.name}</strong><br>
          Queen: ${props.queen_info?.breed}<br>
          Active: ${props.active ? 'Yes' : 'No'}
        `);
      }
    }).addTo(map);
  });
```

### Mapbox GL JS Integration

```javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v11',
  center: [-73.9654, 40.7829],
  zoom: 13
});

map.on('load', () => {
  // Load hives
  fetch('http://localhost:5000/geo/ruches')
    .then(response => response.json())
    .then(geojson => {
      map.addSource('ruches', {
        type: 'geojson',
        data: geojson
      });

      map.addLayer({
        id: 'ruches',
        type: 'circle',
        source: 'ruches',
        paint: {
          'circle-radius': 8,
          'circle-color': '#FFA500',
          'circle-stroke-color': '#FFFFFF',
          'circle-stroke-width': 2
        }
      });
    });
});
```

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000"

# Get all hives
response = requests.get(f"{BASE_URL}/geo/ruches")
geojson = response.json()
print(f"Found {len(geojson['features'])} hives")

# Get hives with filters
params = {
    'active': 'true',
    'cluster': 'true'
}
response = requests.get(f"{BASE_URL}/geo/ruches", params=params)
data = response.json()

# Get single hive
hive_id = 1
response = requests.get(f"{BASE_URL}/geo/ruches/{hive_id}")
hive = response.json()
print(f"Hive: {hive['properties']['name']}")

# Find hives within radius
params = {
    'lat': 40.7829,
    'lon': -73.9654,
    'radius': 1000
}
response = requests.get(f"{BASE_URL}/geo/ruches", params=params)
nearby_hives = response.json()
print(f"Found {len(nearby_hives['features'])} hives within 1km")
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

### 400 Bad Request
Invalid parameters:
```json
{
  "error": "Invalid radius parameters"
}
```

### 404 Not Found
Resource not found:
```json
{
  "error": "Ruche not found"
}
```

### 500 Internal Server Error
Server error:
```json
{
  "error": "Internal server error"
}
```

### 503 Service Unavailable
Database unavailable:
```json
{
  "status": "unhealthy",
  "checks": {
    "database": {
      "status": "unhealthy",
      "message": "Database connection failed"
    }
  }
}
```

## Tips & Best Practices

1. **Use clustering for large datasets**: Add `?cluster=true` when displaying many points on a map
2. **Implement pagination**: For large result sets, consider implementing pagination (future feature)
3. **Cache responses**: Cache GeoJSON responses in your frontend to reduce API calls
4. **Handle errors gracefully**: Always check HTTP status codes and handle errors appropriately
5. **Use HTTPS in production**: Always use HTTPS for secure communication
6. **Respect rate limits**: If rate limiting is implemented, respect the limits

## Performance Considerations

- Radius queries are optimized using PostGIS spatial indexes
- Clustering is performed on the server for better performance
- Consider caching frequently accessed data
- Use appropriate zoom levels and viewport bounds to limit data requests
