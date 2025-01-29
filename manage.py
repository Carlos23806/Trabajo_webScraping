import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
import pymysql
import os
import schedule

def setup_clean_database():
    try:
        print("\n=== Verificando base de datos ===")
        db = pymysql.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = db.cursor()
        
        # Solo crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS webscraping")
        print("Base de datos verificada exitosamente")
        
        db.close()
        return True
    except Exception as e:
        print(f"Error preparando la base de datos: {e}")
        return False

def clean_json():
    try:
        print("\n=== Limpiando archivo JSON anterior ===")
        if os.path.exists('data.json'):
            os.remove('data.json')
            print("Archivo JSON anterior eliminado")
    except Exception as e:
        print(f"Error al limpiar JSON: {e}")

def run_server():
    server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    print("Servidor iniciado en http://localhost:8000/display_data.html")
    server.serve_forever()

def update_data():
    print("\n=== Actualizando datos ===")
    clean_json()
    subprocess.run(["python", "import2.py"])
    subprocess.run(["python", "fetch_data.py"])
    print("Actualización completada")

def main():
    # Configuración inicial
    setup_clean_database()
    
    # Primera ejecución
    update_data()
    
    schedule.every(24).hours.do(update_data)
    
    # Iniciar servicio de email
    import email_sender
    email_thread = threading.Thread(target=email_sender.run_scheduler, daemon=True)
    email_thread.start()
    
    # Iniciar servidor
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Abrir navegador
    time.sleep(1)
    webbrowser.open('http://localhost:8000/display_data.html')
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCerrando el servidor...")

if __name__ == "__main__":
    main()
