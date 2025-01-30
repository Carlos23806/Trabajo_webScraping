import subprocess
import time
import os
import schedule
from db_connection import setup_database
import threading
import email_sender

def setup_clean_database():
    db, cursor = setup_database()
    if db:
        db.close()
        return True
    return False

def update_data():
    print("\n=== Actualizando datos ===")
    subprocess.run(["python", "import2.py"])
    print("Actualización completada")

def main():
    # Configuración inicial
    setup_clean_database()
    
    # Primera ejecución
    update_data()
    
    # Actualizar datos cada 5 minutos
    schedule.every(5).minutes.do(update_data)
    
    # Iniciar servicio de email en un hilo separado
    email_thread = threading.Thread(target=email_sender.run_scheduler, daemon=True)
    email_thread.start()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCerrando el programa...")

if __name__ == "__main__":
    main()
