# database.py
import mysql.connector
from mysql.connector import errorcode


class Database:
    def __init__(self):
        self._connect()
        self._create_tables()

    def _connect(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )

    def _ensure_connection(self):
        try:
            # Always try to ping and reconnect if any error occurs
            self.connection.ping(reconnect=True, attempts=3, delay=2)
        except Exception:
            self._connect()

    def _create_tables(self):
        self._ensure_connection()
        cursor = self.connection.cursor()
        
        # Vehicles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id VARCHAR(36) PRIMARY KEY,
                owner_name VARCHAR(20),
                Plate_number VARCHAR(20),
                MOdel VARCHAR(20),  
                color VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Violations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
            violation_id INT AUTO_INCREMENT PRIMARY KEY,
            vehicle_id VARCHAR(36),
            violation_type VARCHAR(50),
            owner_name VARCHAR(20),
            count INT DEFAULT 0,
            price INT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'unpaid',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                violation_id INT,
                violation_type VARCHAR(50),
                owner_name VARCHAR(20),
                amount INT,
                payment_date DATETIME,
                status VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (violation_id) REFERENCES violations(violation_id)
            )
        """)
        # Blacklist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                blacklist_id VARCHAR(36) PRIMARY KEY,
                driver_name VARCHAR(20),
                plate_number VARCHAR(20),
                reason VARCHAR(100),
                status VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users table for GUI auth
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password_hash VARCHAR(64)
            )
        """)
        
        self.connection.commit()


# Ensure these functions are defined and exported in this file:
def get_violation_statistics():
    db = Database()
    stats = db.get_violation_stats()
    # Convert list of dicts to list of tuples for compatibility
    return [(row['violation_type'], row['count']) for row in stats]

def get_recent_violations(limit=10):
    db = Database()
    rows = db.get_recent_violations(limit)
    # Convert list of dicts to list of tuples for compatibility
    return [(r['violation_id'], r['vehicle_id'], r['violation_type'], r['details'], r['timestamp'], r['driver_id']) for r in rows]

def get_todays_violators_count():
    db = Database()
    return db.get_todays_violators_count()

def get_high_risk_drivers_count():
    db = Database()
    return db.get_high_risk_drivers_count()

def get_active_alerts_count():
    db = Database()
    return db.get_active_alerts_count()
