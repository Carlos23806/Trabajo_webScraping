import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import schedule
from db_connection import get_connection

# Configuración del correo
SENDER_EMAIL = "colvainnovacolvatel@gmail.com"
SENDER_PASSWORD = "dcbk bgzl fxhd dbmj" 
RECEIVER_EMAIL = "cm2873640@gmail.com"

def get_new_records():
    try:
        db = get_connection()
        if not db:
            return None, None, []
        cursor = db.cursor()
        
        query = """
            SELECT id, titulo, objeto, url, fecha_creacion 
            FROM scraped_data 
            WHERE enviado = 0 
            AND objeto IS NOT NULL 
            AND LENGTH(TRIM(objeto)) > 10
            AND objeto != 'Objeto:'
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        return db, cursor, records
    except Exception as e:
        print(f"Error obteniendo registros: {e}")
        if 'db' in locals():
            db.close()
        return None, None, []

def format_email_content(records):
    if not records:
        html_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .message { padding: 20px; background-color: #f8f9fa; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="message">
                <h2>Actualización de Convocatorias ETB</h2>
                <p>No se encontraron convocatorias nuevas en este momento.</p>
                <p>Fecha de verificación: %s</p>
            </div>
        </body>
        </html>
        """ % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return html_template

    html = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>Nuevas convocatorias de ETB</h2>
        <table>
            <tr>
                <th>Título</th>
                <th>Objeto</th>
                <th>URL</th>
                <th>Fecha</th>
            </tr>
    """
    
    for record in records:
        html += f"""
            <tr>
                <td>{record[1]}</td>
                <td>{record[2]}</td>
                <td><a href="{record[3]}">{record[3]}</a></td>
                <td>{record[4]}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    return html

def send_email(records):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    if not records:
        msg['Subject'] = f"ETB - Sin nuevas convocatorias - {datetime.now().strftime('%Y-%m-%d')}"
    else:
        msg['Subject'] = f"Nuevos registros ETB - {datetime.now().strftime('%Y-%m-%d')}"

    html_content = format_email_content(records)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✓ Email enviado exitosamente {'(sin nuevos registros)' if not records else f'con {len(records)} registros'}")
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def update_sent_status(db, cursor, records):
    try:
        if not records:
            return
        ids = [str(record[0]) for record in records]
        query = """
            UPDATE scraped_data 
            SET enviado = 1 
            WHERE id IN ({}) 
            AND enviado = 0
        """.format(','.join(ids))
        cursor.execute(query)
        db.commit()
    except Exception as e:
        print(f"✗ Error actualizando estados: {e}")
        db.rollback()

def check_and_send():
    print(f"\n=== Verificación de registros {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        db, cursor, records = get_new_records()
        if not db or not cursor:
            print("✗ Error de conexión a la base de datos")
            return
        if send_email(records):
            if records:
                update_sent_status(db, cursor, records)
    except Exception as e:
        print(f"✗ Error en check_and_send: {e}")
    finally:
        if 'db' in locals() and db:
            cursor.close()
            db.close()

def run_scheduler():
    print("\n=== Iniciando servicio de notificaciones ===")
    print("• El correo se enviará todos los días a las 8:00 AM")
    print("• Presione Ctrl+C para detener el servicio")
    print("-" * 50)
    
    schedule.every().day.at("20:21").do(check_and_send)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Revisar cada minuto si es la hora de ejecución
    except KeyboardInterrupt:
        print("\n=== Servicio de notificaciones detenido ===")

if __name__ == "_main_":
    run_scheduler()