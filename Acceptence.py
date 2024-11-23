import psycopg2

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


# Function for ride acceptance
def accept_ride():
    try:
        ride_id = int(input("Enter Ride ID: "))
        driver_id = int(input("Enter Driver ID: "))

        cur = conn.cursor()
        conn.autocommit = False  # Start a transaction

        # Lock the ride to prevent other drivers from accepting it
        cur.execute("SELECT * FROM \"Ride\" WHERE \"RideID\" = %s AND \"Status\" = 'Requested' FOR UPDATE;", (ride_id,))
        ride = cur.fetchone()
        if not ride:
            conn.rollback()
            print("Error: Ride not available or already accepted")
            return

        # Update ride status to 'Accepted' and assign the driver
        cur.execute("""
            UPDATE "Ride" 
            SET "Status" = 'Accepted', "DriverID" = %s 
            WHERE "RideID" = %s;
        """, (driver_id, ride_id))

        # Update driver availability to 'Offline'
        cur.execute("""
            UPDATE "Driver" 
            SET "AvailabilityStatus" = 'Offline' 
            WHERE "DriverID" = %s AND "AvailabilityStatus" = 'Online';
        """, (driver_id,))
        if cur.rowcount == 0:
            conn.rollback()
            print("Error: Driver is not available")
            return

        conn.commit()
        print(f"Ride ID {ride_id} successfully accepted by Driver ID {driver_id}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()


# Main function
if __name__ == "__main__":
    print("=== Ride Acceptance System ===")
    accept_ride()