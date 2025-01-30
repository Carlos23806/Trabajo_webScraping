import pymysql
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

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='webscraping'
    )

def get_new_records():
    try:
        db = get_connection()
        if not db:
            return None, None, []
        cursor = db.cursor()
        
        # Añadido logging para verificar la consulta
        print("Ejecutando consulta para obtener registros no enviados...")
        
        query = """
            SELECT id, titulo, objeto, url, fecha_creacion 
            FROM scraped_data 
            WHERE enviado = 0 
            AND objeto IS NOT NULL 
            AND LENGTH(TRIM(objeto)) > 10
            AND objeto != 'Objeto:'
        """
        
        print(f"Query: {query}")
        cursor.execute(query)
        records = cursor.fetchall()
        
        # Añadido logging para verificar resultados
        print(f"Registros encontrados: {len(records)}")
        for record in records:
            print(f"ID: {record[0]}, enviado: 0, título: {record[1]}")
            
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

    # Si hay registros, usar el formato existente
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
        
        # Verificar el estado actual antes de actualizar
        verify_query = f"SELECT id, enviado FROM scraped_data WHERE id IN ({','.join(ids)})"
        print(f"Verificando estado actual: {verify_query}")
        cursor.execute(verify_query)
        current_states = cursor.fetchall()
        for state in current_states:
            print(f"Estado actual - ID: {state[0]}, enviado: {state[1]}")
        
        # Actualizar solo si el estado es 0
        query = """
            UPDATE scraped_data 
            SET enviado = 1 
            WHERE id IN ({}) 
            AND enviado = 0
        """.format(','.join(ids))
        
        print(f"Ejecutando actualización: {query}")
        cursor.execute(query)
        db.commit()
        
        # Verificar después de la actualización
        cursor.execute(verify_query)
        updated_states = cursor.fetchall()
        print("\nEstados después de la actualización:")
        for state in updated_states:
            print(f"ID: {state[0]}, enviado: {state[1]}")
            
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
            print("✓ Email enviado exitosamente")
            if records:
                update_sent_status(db, cursor, records)
        else:
            print("✗ Error al enviar email")
            
    except Exception as e:
        print(f"✗ Error en check_and_send: {e}")
    finally:
        if 'db' in locals() and db:
            cursor.close()
            db.close()

def run_scheduler():
    print("\n=== Iniciando servicio de notificaciones ===")
    print("• Se verificarán nuevos registros cada 20 minutos")
    print("• Presione Ctrl+C para detener el servicio")
    print("-" * 50)
    
    # Ejecutar inmediatamente la primera vez
    check_and_send()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n=== Servicio de notificaciones detenido ===")

if __name__ == "__main__":
    run_scheduler()