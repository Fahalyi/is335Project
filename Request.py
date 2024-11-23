import psycopg2
import math
from opencage.geocoder import OpenCageGeocode

# Database connection parameters
host = "localhost"
database = "copy"
user = "postgres"
password = "aa"
port_id = 5432

# Establish the database connection
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port_id
    )
    print("Connection successful")
except Exception as error:
    print(f"Error: {error}")
    exit()

# Function to calculate distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Function to geocode an address using OpenCage API
def get_lat_lon(address, api_key):
    geocoder = OpenCageGeocode(api_key)
    results = geocoder.geocode(address)
    if results:
        lat = results[0]['geometry']['lat']
        lon = results[0]['geometry']['lng']
        return lat, lon
    else:
        return None, None

# Function to calculate fare
def calculate_fare(distance_km):
    base_fare = 5.00  # Base fare in currency
    rate_per_km = 2.00  # Rate per kilometer
    return base_fare + (distance_km * rate_per_km)

# Function to calculate duration
def calculate_duration(distance_km):
    average_speed_kmh = 40  # Average speed in km/h
    return distance_km / average_speed_kmh * 60  # Duration in minutes

# OpenCage API key
api_key = "7efdc45da83b436fa25920b5e367f6fe"  # Replace with your OpenCage API key

# Function to request a ride
def request_ride():
    rider_id = int(input("Enter Rider ID: "))
    pickup_address = input("Enter Pickup Address: ")
    dropoff_address = input("Enter Dropoff Address: ")

    # Geocode the addresses
    pickup_lat, pickup_lon = get_lat_lon(pickup_address, api_key)
    dropoff_lat, dropoff_lon = get_lat_lon(dropoff_address, api_key)

    if not (pickup_lat and pickup_lon and dropoff_lat and dropoff_lon):
        print("Error: Could not retrieve latitude and longitude for one or both addresses")
        return

    # Calculate distance
    distance_km = haversine(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)

    # Calculate fare and duration
    fare = calculate_fare(distance_km)
    duration = calculate_duration(distance_km)

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO "Ride" ("RiderID", "PickupAddress", "DropoffAddress", "Distance", "Duration", 
                                "Fare", "Status", "PickupLatitude", "PickupLongitude", "DropoffLatitude", "DropoffLongitude")
            VALUES (%s, %s, %s, %s, %s, %s, 'Requested', %s, %s, %s, %s) RETURNING "RideID";
        """, (rider_id, pickup_address, dropoff_address, distance_km, duration, fare,
              pickup_lat, pickup_lon, dropoff_lat, dropoff_lon))
        ride_id = cur.fetchone()[0]
        conn.commit()
        print(f"Ride requested successfully. Ride ID: {ride_id}, Distance: {distance_km:.2f} km, Duration: {duration:.2f} mins, Fare: ${fare:.2f}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

# Main function
if __name__ == "__main__":
    print("=== Ride Request System ===")
    request_ride()
