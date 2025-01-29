import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
import pymysql
import os

def setup_clean_database():
    try:
        print("\n=== Limpiando y preparando base de datos ===")
        db = pymysql.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = db.cursor()
        
        # Eliminar y recrear la base de datos
        #cursor.execute("DROP DATABASE IF EXISTS webscraping")
        cursor.execute("CREATE DATABASE IF NOT EXISTS webscraping")
        print("Base de datos recreada exitosamente")
        
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

def main():
    # Limpiar JSON anterior
    clean_json()
    
    # Limpiar y preparar base de datos
    if not setup_clean_database():
        print("Error: No se pudo preparar la base de datos")
        return
    
    # Ejecutar scripts de scraping y generación de JSON
    print("\n=== Iniciando web scraping ===")
    subprocess.run(["python", "import2.py"])
    
    print("\n=== Generando nuevo JSON ===")
    subprocess.run(["python", "fetch_data.py"])
    
    print("\n=== Iniciando servicio de email ===")
    # Iniciar el enviador de correos en un hilo separado
    import email_sender
    email_thread = threading.Thread(target=email_sender.run_scheduler, daemon=True)
    email_thread.start()
    
    # Iniciar servidor en un hilo separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Esperar un momento para que el servidor inicie
    time.sleep(1)
    
    # Abrir el navegador
    webbrowser.open('http://localhost:8000/display_data.html')
    
    try:
        # Mantener el programa corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCerrando el servidor...")

if __name__ == "__main__":
    main()
