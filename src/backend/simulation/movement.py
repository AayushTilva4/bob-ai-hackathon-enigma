"""
Deterministic vessel movement along predefined routes.

Progression is a deterministic calculation along predefined route waypoints.
No real marine physics, hydrodynamics, wind, radar, or live AIS are used.
"""

from typing import Any


def parse_route_coordinates(route_points: dict | list | None) -> list[tuple[float, float]]:
    """
    Extract a list of (latitude, longitude) tuples from various route formats:
    - GeoJSON LineString: {"type": "LineString", "coordinates": [[lng, lat], ...]}
    - List of dicts: [{"lat": 1.28, "lng": 103.70}, ...]
    - List of pairs: [[lng, lat], ...]
    """
    if not route_points:
        # Default fallback approach waypoints if none defined
        return [(1.25, 103.65), (1.28, 103.75), (1.30, 103.82)]

    coords: list[tuple[float, float]] = []

    # Handle GeoJSON format
    if isinstance(route_points, dict) and "coordinates" in route_points:
        raw_coords = route_points["coordinates"]
        for pt in raw_coords:
            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                # GeoJSON coordinates are [longitude, latitude]
                coords.append((float(pt[1]), float(pt[0])))
        return coords if coords else [(1.25, 103.65), (1.30, 103.82)]

    # Handle list of coordinate points
    if isinstance(route_points, list):
        for pt in route_points:
            if isinstance(pt, dict):
                lat = float(pt.get("lat", pt.get("latitude", 0.0)))
                lng = float(pt.get("lng", pt.get("lon", pt.get("longitude", 0.0))))
                coords.append((lat, lng))
            elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
                coords.append((float(pt[1]), float(pt[0])))

    return coords if coords else [(1.25, 103.65), (1.30, 103.82)]


def interpolate_position(
    coordinates: list[tuple[float, float]], progress: float
) -> tuple[float, float]:
    """
    Deterministically interpolate a (lat, lng) position along waypoints
    given a progress fraction in [0.0, 1.0].
    """
    if not coordinates:
        return (1.28, 103.75)
    if len(coordinates) == 1 or progress <= 0.0:
        return coordinates[0]
    if progress >= 1.0:
        return coordinates[-1]

    # Map progress to segments
    num_segments = len(coordinates) - 1
    scaled = progress * num_segments
    segment_idx = min(int(scaled), num_segments - 1)
    segment_progress = scaled - segment_idx

    lat1, lng1 = coordinates[segment_idx]
    lat2, lng2 = coordinates[segment_idx + 1]

    lat = round(lat1 + (lat2 - lat1) * segment_progress, 6)
    lng = round(lng1 + (lng2 - lng1) * segment_progress, 6)
    return (lat, lng)
