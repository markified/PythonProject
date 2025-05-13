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
                driver_id VARCHAR(20),
                speed FLOAT,
                latitude FLOAT,
                longitude FLOAT,
                timestamp DATETIME,
                signal_status VARCHAR(10)
            )
        """)
        
        # Violations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                violation_id INT AUTO_INCREMENT PRIMARY KEY,
                vehicle_id VARCHAR(36),
                violation_type VARCHAR(50),
                details TEXT,
                timestamp DATETIME,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
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
    
    
# Insert vehicle data
    def insert_vehicle_data(self, data):
        self._ensure_connection()
        cursor = self.connection.cursor()
        query = """
            INSERT INTO vehicles 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['vehicle_id'],
            data['driver_id'],
            data['speed'],
            data['location'][0],
            data['location'][1],
            data['timestamp'],
            data['signal_status']
        ))
        self.connection.commit()
# Insert violations
    def insert_violations(self, vehicle_id, violations):
        self._ensure_connection()
        cursor = self.connection.cursor()
        query = """
            INSERT INTO violations 
            (vehicle_id, violation_type, details, timestamp)
            VALUES (%s, %s, %s, NOW())
        """
        for violation in violations:
            cursor.execute(query, (
                vehicle_id,
                violation['type'],
                violation['details']
            ))
        self.connection.commit()
  # Get violation statistics  
    def get_violation_stats(self):
        self._ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT violation_type, COUNT(*) as count 
            FROM violations 
            GROUP BY violation_type
        """)
        return cursor.fetchall()
  # Get today's violators count  
    def get_recent_violations(self, limit=10):
        self._ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.*, vhc.driver_id 
            FROM violations v
            JOIN vehicles vhc USING (vehicle_id)
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
# Get today's violators count
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='vehicle_monitoring'
    )
# Get today's violators count
def get_violation_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT violation_type, COUNT(*) FROM violations GROUP BY violation_type")
    result = cursor.fetchall()
    conn.close()
    return result
# Get recent violations
def get_recent_violations(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.violation_id, v.vehicle_id, v.violation_type, v.details, v.timestamp, vhc.driver_id
        FROM violations v
        JOIN vehicles vhc ON v.vehicle_id = vhc.vehicle_id
        ORDER BY v.timestamp DESC LIMIT %s
    """, (limit,))
    result = cursor.fetchall()
    conn.close()
    return result
# Get today's violators count
def get_todays_violators_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT vhc.driver_id)
        FROM violations v
        JOIN vehicles vhc ON v.vehicle_id = vhc.vehicle_id
        WHERE DATE(v.timestamp) = CURDATE()
    """)
    result = cursor.fetchone()[0]
    conn.close()
    return result
# Get high-risk drivers count
def get_high_risk_drivers_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT driver_id, COUNT(*) as vcount
            FROM vehicles v
            JOIN violations vl ON v.vehicle_id = vl.vehicle_id
            GROUP BY driver_id
            HAVING vcount > 3
        ) as risky
    """)
    result = cursor.fetchone()[0]
    conn.close()
    return result
# Get active alerts count
def get_active_alerts_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM violations
        WHERE timestamp >= NOW() - INTERVAL 1 HOUR
    """)
    result = cursor.fetchone()[0]
    conn.close()
    return result