import requests
from bs4 import BeautifulSoup
import pymysql
import sys
import re
import time

def setup_database():
    try:
        print("Conectando al servidor MySQL con pymysql...")
        db = pymysql.connect(
            host='localhost',
            user='root',
            password=''
        )
        print("Conexión exitosa")
        cursor = db.cursor()
        
        # Crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS webscraping")
        cursor.execute("USE webscraping")
        
        # Crear la tabla si no existe
        print("Verificando tabla...")
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
        print(f"Error: {e}")
        sys.exit(1)

def extract_invitation_number(title):
    # Buscar un patrón de 10 dígitos después de "No."
    match = re.search(r'No\.\s*(\d{10})', title)
    return match.group(1) if match else None

def is_invitation_exists(cursor, invitation_number):
    if not invitation_number:
        return False
    cursor.execute("SELECT COUNT(*) FROM scraped_data WHERE titulo LIKE %s", f'%{invitation_number}%')
    count = cursor.fetchone()[0]
    return count > 0

# URL de la página que deseas scrapea
url = "https://etb.com/Corporativo/abastecimiento2.aspx#estu"

# Realizar la solicitud GET a la página
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML de la página
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Buscar todos los contenedores relevantes
    contenedores = soup.find_all("div", class_="faq2")  # Si las etiquetas <p> están dentro de divs, ajusta el selector aquí.
    
    # Conectar a la base de datos MySQL
    print("intentando la conexion con la base de datos")
    db, cursor = setup_database()

    for contenedor in contenedores:
        Titulo = contenedor.find("h4").text.strip() if contenedor.find("h4") else "No encontrado"
        
        # Extraer y verificar el número de invitación
        invitation_number = extract_invitation_number(Titulo)
        if invitation_number and is_invitation_exists(cursor, invitation_number):
            print(f"Invitación {invitation_number} ya existe en la base de datos. Saltando...")
            continue

        print(f"Nuevo registro encontrado - Titulo: {Titulo}")
        
        # Modificar la lógica para obtener el objeto
        parrafos = contenedor.find_all("p")
        objeto_completo = ""
        
        for parrafo in parrafos:
            texto = parrafo.text.strip()
            if texto.lower() != "objeto:" and len(texto) > 10:
                objeto_completo = texto
                break
                
        if not objeto_completo:
            continue  # Saltar este registro si no hay objeto válido
            
        # Buscar el enlace del botón "Ver más" dentro del mismo contenedor
        boton = contenedor.find("a", href=True)
        link = boton["href"] if boton else "No encontrado"
        
        # Imprimir la información
        print(f"Objeto: {objeto_completo}")    
        print(f"URL: https://etb.com/Corporativo/{link}")
        
        # Modificar la inserción para ignorar duplicados
        cursor.execute("""
        INSERT IGNORE INTO scraped_data (titulo, objeto, url, enviado)
        VALUES (%s, %s, %s, 0)
        """, (Titulo, objeto_completo, f"https://etb.com/Corporativo/{link}"))

    # Confirmar los cambios en la base de datos
    db.commit()

    # Cerrar la conexión a la base de datos
    cursor.close()
    db.close()
else:
    print(f"Error al acceder a la página. Código de estado: {response.status_code}")
