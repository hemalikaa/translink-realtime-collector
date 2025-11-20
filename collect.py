import requests
from google.transit import gtfs_realtime_pb2
import json
import os
from datetime import datetime

VEHICLE_POSITIONS_URL = "https://gtfs.translink.ca/v2/gtfsposition"
TRIP_UPDATES_URL = "https://gtfs.translink.ca/v2/gtfsrealtime"

def collect_data():
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Collect vehicle positions
    try:
        response = requests.get(VEHICLE_POSITIONS_URL, timeout=10)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                v = entity.vehicle
                vehicles.append({
                    'trip_id': v.trip.trip_id,
                    'route_id': v.trip.route_id,
                    'vehicle_id': v.vehicle.id,
                    'latitude': v.position.latitude,
                    'longitude': v.position.longitude,
                    'timestamp': v.timestamp,
                    'current_stop_sequence': v.current_stop_sequence
                })
        
        with open(f"data/vehicles_{timestamp}.json", 'w') as f:
            json.dump(vehicles, f)
        print(f"Collected {len(vehicles)} vehicle positions")
            
    except Exception as e:
        print(f"Error fetching vehicles: {e}")
    
    # Collect trip updates
    try:
        response = requests.get(TRIP_UPDATES_URL, timeout=10)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        trip_updates = []
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                tu = entity.trip_update
                for stop_update in tu.stop_time_update:
                    trip_updates.append({
                        'trip_id': tu.trip.trip_id,
                        'route_id': tu.trip.route_id,
                        'stop_id': stop_update.stop_id,
                        'stop_sequence': stop_update.stop_sequence,
                        'arrival_delay': stop_update.arrival.delay if stop_update.HasField('arrival') else None,
                        'departure_delay': stop_update.departure.delay if stop_update.HasField('departure') else None,
                        'timestamp': tu.timestamp
                    })
        
        with open(f"data/trips_{timestamp}.json", 'w') as f:
            json.dump(trip_updates, f)
        print(f"Collected {len(trip_updates)} trip updates")
            
    except Exception as e:
        print(f"Error fetching trip updates: {e}")

if __name__ == "__main__":
    collect_data()
