import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def mark_attendance(roll):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attendance (roll_number, status) VALUES (%s, %s)",
        (roll, "Present")
    )

def log_cheating(roll, cheat_type):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO cheating_logs (roll_number, type) VALUES (%s, %s)",
        (roll, cheat_type)
    )

    conn.commit()
    cursor.close()
    conn.close()