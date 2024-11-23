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


# Function to retrieve ride details
def get_ride_details():
    try:
        ride_id = int(input("Enter Ride ID: "))

        cur = conn.cursor()

        # Fetch ride details
        cur.execute("""
            SELECT r."RideID", r."Status", r."PickupAddress", r."DropoffAddress", 
                   r."Distance", r."Fare", u1."Name" AS "RiderName", u1."Contact" AS "RiderContact", 
                   u2."Name" AS "DriverName", u2."Contact" AS "DriverContact", 
                   v."Make", v."Model", v."PlateNumber"
            FROM "Ride" r
            LEFT JOIN "User" u1 ON r."RiderID" = u1."UserID"  -- Join RiderID to UserID
            LEFT JOIN "Driver" d ON r."DriverID" = d."DriverID"
            LEFT JOIN "User" u2 ON d."DriverID" = u2."UserID"  -- Join DriverID to UserID
            LEFT JOIN "Vehicle" v ON d."DriverID" = v."DriverID"
            WHERE r."RideID" = %s;
        """, (ride_id,))
        ride = cur.fetchone()

        if not ride:
            print("Error: Ride not found.")
            return

        # Parse the result into a structured response
        response = {
            "RideID": ride[0],
            "Status": ride[1],
            "PickupAddress": ride[2],
            "DropoffAddress": ride[3],
            "Distance": ride[4],
            "Fare": ride[5],
            "Rider": {
                "Name": ride[6] if ride[6] else "N/A",
                "Contact": ride[7] if ride[7] else "N/A"
            },
            "Driver": {
                "Name": ride[8] if ride[8] else "N/A",
                "Contact": ride[9] if ride[9] else "N/A",
                "Vehicle": {
                    "Make": ride[10] if ride[10] else "N/A",
                    "Model": ride[11] if ride[11] else "N/A",
                    "PlateNumber": ride[12] if ride[12] else "N/A"
                } if ride[8] else None
            } if ride[8] else None
        }

        print("Ride Details:")
        print(response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()



# Main function
if __name__ == "__main__":
    print("=== Ride Details Retrieval System ===")
    get_ride_details()