import pytest
from src.data_collection.collector import fetch_vehicle_data

def test_fetch_returns_vehicles():
    vehicles = fetch_vehicle_data()
    assert len(vehicles) > 0
    assert all('bike_id' in v for v in vehicles)

def test_database_insertion():
    # Test that data is saved correctly
    pass
