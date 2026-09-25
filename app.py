from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)


# =========================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "booking_db"
}


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

    return connection


# =========================================================
# CREATE TABLE
# =========================================================

def create_table():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (

                id INT AUTO_INCREMENT PRIMARY KEY,

                customer_name VARCHAR(150) NOT NULL,

                phone VARCHAR(10) NOT NULL,

                service VARCHAR(100) NOT NULL,

                amount DECIMAL(10,2) NOT NULL,

                payment_method VARCHAR(20) NOT NULL,

                booking_date DATE NOT NULL,

                booking_time TIME NOT NULL

            )
        """)

        connection.commit()

        print("Bookings table is ready.")

    except Error as e:

        print("Database table error:", e)

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# BOOKING API
# =========================================================

@app.route("/book", methods=["POST"])
def book():

    connection = None
    cursor = None

    try:

        # ---------------------------------------------
        # GET DATA FROM JAVASCRIPT
        # ---------------------------------------------

        data = request.get_json()

        print("Received booking:", data)


        if not data:

            return jsonify({
                "success": False,
                "message": "No booking data received."
            }), 400


        # ---------------------------------------------
        # GET VALUES
        # ---------------------------------------------

        customer_name = data.get(
            "customer_name", ""
        ).strip()

        phone = data.get(
            "phone", ""
        ).strip()

        service = data.get(
            "service", ""
        ).strip()

        amount = data.get(
            "amount", ""
        )

        payment_method = data.get(
            "payment_method", ""
        ).strip()


        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if not customer_name:

            return jsonify({
                "success": False,
                "message": "Customer name is required."
            }), 400


        if not phone:

            return jsonify({
                "success": False,
                "message": "Phone number is required."
            }), 400


        if not phone.isdigit() or len(phone) != 10:

            return jsonify({
                "success": False,
                "message": "Enter a valid 10-digit phone number."
            }), 400


        if not service:

            return jsonify({
                "success": False,
                "message": "Please select a service."
            }), 400


        # ---------------------------------------------
        # AMOUNT VALIDATION
        # ---------------------------------------------

        try:

            amount = float(amount)

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message": "Please enter a valid amount."
            }), 400


        if amount <= 0:

            return jsonify({
                "success": False,
                "message": "Amount must be greater than 0."
            }), 400


        # ---------------------------------------------
        # PAYMENT VALIDATION
        # ---------------------------------------------

        if payment_method not in ["GPay", "Cash"]:

            return jsonify({
                "success": False,
                "message": "Please select GPay or Cash."
            }), 400


        # ---------------------------------------------
        # DATE AND TIME
        # ---------------------------------------------

        now = datetime.now()

        booking_date = now.date()

        booking_time = now.time()


        # ---------------------------------------------
        # CONNECT MYSQL
        # ---------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor()


        # ---------------------------------------------
        # INSERT BOOKING
        # ---------------------------------------------

        query = """
            INSERT INTO bookings
            (
                customer_name,
                phone,
                service,
                amount,
                payment_method,
                booking_date,
                booking_time
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """


        values = (
            customer_name,
            phone,
            service,
            amount,
            payment_method,
            booking_date,
            booking_time
        )


        cursor.execute(query, values)


        # ---------------------------------------------
        # GET BOOKING ID
        # ---------------------------------------------

        booking_id = cursor.lastrowid


        # ---------------------------------------------
        # SAVE
        # ---------------------------------------------

        connection.commit()


        print("----------------------------------------")
        print("BOOKING SAVED SUCCESSFULLY")
        print("Booking ID:", booking_id)
        print("Customer:", customer_name)
        print("Phone:", phone)
        print("Service:", service)
        print("Amount:", amount)
        print("Payment:", payment_method)
        print("----------------------------------------")


        # ---------------------------------------------
        # RESPONSE
        # ---------------------------------------------

        return jsonify({

            "success": True,

            "booking_id": booking_id,

            "message":
                f"Booking successful! Booking ID: {booking_id}"

        }), 200


    except Error as e:

        print("----------------------------------------")
        print("MYSQL ERROR")
        print(e)
        print("----------------------------------------")


        if connection:

            connection.rollback()


        return jsonify({

            "success": False,

            "message":
                "Database error. Please try again."

        }), 500


    except Exception as e:

        print("----------------------------------------")
        print("SERVER ERROR")
        print(e)
        print("----------------------------------------")


        if connection:

            connection.rollback()


        return jsonify({

            "success": False,

            "message":
                "Something went wrong. Please try again."

        }), 500


    finally:

        if cursor:

            cursor.close()


        if connection and connection.is_connected():

            connection.close()


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    print("")
    print("==========================================")
    print("       CUSTOMER BOOKING SYSTEM")
    print("==========================================")

    # Create table automatically
    create_table()

    print("Server starting...")
    print("Open: http://127.0.0.1:5000")

    print("==========================================")


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )