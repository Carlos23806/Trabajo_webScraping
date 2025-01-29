import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import schedule

# Configuración del correo
SENDER_EMAIL = "cm2873640@gmail.com"
SENDER_PASSWORD = "nqqa nxws ywcu fhaf" 
RECEIVER_EMAIL = "ammastercraft@gmail.com"

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='webscraping'
    )

def get_new_records():
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT id, titulo, objeto, url, fecha_creacion 
            FROM scraped_data 
            WHERE enviado = FALSE
        """)
        records = cursor.fetchall()
        return db, cursor, records
    except Exception as e:
        print(f"Error obteniendo registros: {e}")
        db.close()
        return None, None, []

def format_email_content(records):
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
        <h2>Nuevos registros de ETB</h2>
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
    if not records:
        print("No hay nuevos registros para enviar")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"Nuevos registros ETB - {datetime.now().strftime('%Y-%m-%d')}"

    html_content = format_email_content(records)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def update_sent_status(db, cursor, records):
    try:
        for record in records:
            cursor.execute("""
                UPDATE scraped_data 
                SET enviado = TRUE 
                WHERE id = %s
            """, (record[0],))
        db.commit()
        print(f"Actualizados {len(records)} registros como enviados")
    except Exception as e:
        print(f"Error actualizando estados: {e}")
        db.rollback()

def check_and_send():
    print(f"\nVerificando nuevos registros - {datetime.now()}")
    db, cursor, records = get_new_records()
    
    if records and send_email(records):
        update_sent_status(db, cursor, records)
    
    if db:
        db.close()

def run_scheduler():
    # Ejecutar inmediatamente la primera vez
    check_and_send()
    
    # Programar para ejecutar cada 24 horas
    schedule.every(24).hours.do(check_and_send)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
