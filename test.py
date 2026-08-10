from database import get_connection

conn = get_connection()

if conn:
    print("Database Connected!")
    conn.close()
else:
    print("Connection Failed!")