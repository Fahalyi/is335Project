import psycopg2
import random

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

# Function for ride completion and payment
def complete_ride():
    try:
        ride_id = int(input("Enter Ride ID: "))
        payment_method = input("Enter Payment Method (Credit Card/Cash): ")

        cur = conn.cursor()
        conn.autocommit = False  # Start a transaction

        # Lock the ride to ensure no concurrent updates
        cur.execute("SELECT * FROM \"Ride\" WHERE \"RideID\" = %s AND \"Status\" = 'Accepted' FOR UPDATE;", (ride_id,))
        ride = cur.fetchone()
        if not ride:
            conn.rollback()
            print("Error: Ride not available or already completed.")
            return

        # Retrieve the fare from the ride
        fare = ride[9]

        # Update the ride status to 'Completed'
        cur.execute("""
            UPDATE "Ride" 
            SET "Status" = 'Completed' 
            WHERE "RideID" = %s;
        """, (ride_id,))

        # Simulate payment processing
        payment_status = random.choice(["Success", "Failure"])
        if payment_status == "Failure":
            raise Exception("Payment processing failed.")

        # Insert payment record
        cur.execute("""
            INSERT INTO "Payment" ("RideID", "Amount", "PaymentMethod", "Timestamp")
            VALUES (%s, %s, %s, NOW());
        """, (ride_id, fare, payment_method))

        conn.commit()
        print(f"Ride ID {ride_id} successfully completed. Fare: {fare:.2f}, Payment Status: {payment_status}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()

# Main function
if __name__ == "__main__":
    print("=== Ride Completion and Payment System ===")
    complete_ride()