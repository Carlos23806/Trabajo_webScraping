import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': 3307
}

def get_connection(database='webscraping'):
    try:
        connection = pymysql.connect(
            **DB_CONFIG,
            database=database if database else None
        )
        return connection
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def setup_database():
    try:
        print("Conectando al servidor MySQL...")
        db = get_connection(database=None)
        if not db:
            return None, None
            
        cursor = db.cursor()
        
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS webscraping")
        cursor.execute("USE webscraping")
        
        # Crear tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(500) unique,
            objeto TEXT,
            url VARCHAR(500),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enviado INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        db.commit()
        print("Base de datos verificada correctamente")
        return db, cursor
        
    except Exception as e:
        print(f"Error configurando base de datos: {e}")
        if 'db' in locals():
            db.close()
        return None, None
