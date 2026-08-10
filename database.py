import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",   # Try this
            database="hostel_management"
        )
        print("✅ Connected database:", conn.database)
        return conn

    except mysql.connector.Error as err:
        print("❌", err)
        return None