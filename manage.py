import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

def run_server():
    server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    print("Servidor iniciado en http://localhost:8000/display_data.html")
    server.serve_forever()

def main():
    # Ejecutar scripts de scraping y generación de JSON
    print("Ejecutando import2.py...")
    subprocess.run(["python", "import2.py"])
    
    print("Ejecutando fetch_data.py...")
    subprocess.run(["python", "fetch_data.py"])
    
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
