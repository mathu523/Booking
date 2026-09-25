from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import Error
from datetime import datetime
import os

app = Flask(__name__)


# =========================================================
# POSTGRESQL DATABASE CONFIGURATION
# =========================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set.")

    connection = psycopg2.connect(DATABASE_URL)

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

                id SERIAL PRIMARY KEY,

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

    except Exception as e:

        print("Database table error:", e)

    finally:

        if cursor:
            cursor.close()

        if connection:
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

        # GET DATA FROM JAVASCRIPT
        data = request.get_json()

        print("Received booking:", data)

        if not data:

            return jsonify({
                "success": False,
                "message": "No booking data received."
            }), 400


        # =================================================
        # GET VALUES
        # =================================================

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


        # =================================================
        # VALIDATION
        # =================================================

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
                "message":
                    "Enter a valid 10-digit phone number."
            }), 400


        if not service:

            return jsonify({
                "success": False,
                "message": "Please select a service."
            }), 400


        # =================================================
        # AMOUNT VALIDATION
        # =================================================

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
                "message":
                    "Amount must be greater than 0."
            }), 400


        # =================================================
        # PAYMENT VALIDATION
        # =================================================

        if payment_method not in ["GPay", "Cash"]:

            return jsonify({
                "success": False,
                "message":
                    "Please select GPay or Cash."
            }), 400


        # =================================================
        # DATE AND TIME
        # =================================================

        now = datetime.now()

        booking_date = now.date()

        booking_time = now.time()


        # =================================================
        # CONNECT POSTGRESQL
        # =================================================

        connection = get_db_connection()

        cursor = connection.cursor()


        # =================================================
        # INSERT BOOKING
        # =================================================

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
            RETURNING id
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


        cursor.execute(
            query,
            values
        )


        # =================================================
        # GET BOOKING ID
        # =================================================

        booking_id = cursor.fetchone()[0]


        # =================================================
        # SAVE
        # =================================================

        connection.commit()


        # =================================================
        # PRINT SUCCESS
        # =================================================

        print("----------------------------------------")

        print("BOOKING SAVED SUCCESSFULLY")

        print("Booking ID:", booking_id)

        print("Customer:", customer_name)

        print("Phone:", phone)

        print("Service:", service)

        print("Amount:", amount)

        print("Payment:", payment_method)

        print("----------------------------------------")


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "booking_id": booking_id,

            "message":
                f"Booking successful! Booking ID: {booking_id}"

        }), 200


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except Exception as e:

        print("----------------------------------------")

        print("POSTGRESQL / SERVER ERROR")

        print(e)

        print("----------------------------------------")


        if connection:

            connection.rollback()


        return jsonify({

            "success": False,

            "message":
                "Database error. Please try again."

        }), 500


    finally:

        if cursor:

            cursor.close()


        if connection:

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

    print("==========================================")


    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),

        debug=False

    )