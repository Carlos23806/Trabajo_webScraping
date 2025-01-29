import requests
from bs4 import BeautifulSoup
import pymysql
import sys
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
        
        # Eliminar la base de datos si existe
        print("Eliminando base de datos si existe...")
        cursor.execute("DROP DATABASE IF EXISTS webscraping")
        
        # Crear la base de datos nueva
        print("Creando nueva base de datos...")
        cursor.execute("CREATE DATABASE webscraping")
        cursor.execute("USE webscraping")
        
        # Crear la tabla desde cero
        print("Creando tabla...")
        cursor.execute("""
        CREATE TABLE scraped_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(500),
            objeto TEXT,
            url VARCHAR(500),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        db.commit()
        print("Base de datos configurada correctamente")
        return db, cursor
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

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
        # Buscar todas las etiquetas <p> dentro del contenedor
        Titulo = contenedor.find("h4").text.strip() if contenedor.find("h4") else "No encontrado"
        print(f"Titulo: {Titulo}")
        parrafos = contenedor.find_all("p")
        
        # Obtener el texto completo del objeto, ignorando el párrafo que solo contiene "Objeto:"
        objeto = None
        for parrafo in parrafos:
            texto = parrafo.text.strip()
            if texto and texto.lower() != "objeto:":
                objeto = texto
                break
        
        if not objeto:
            objeto = "No encontrado"
            
        # Buscar el enlace del botón "Ver más" dentro del mismo contenedor
        boton = contenedor.find("a", href=True)
        link = boton["href"] if boton else "No encontrado"
        
        # Imprimir la información
        print(f"Objeto: {objeto}")    
        print(f"URL: https://etb.com/Corporativo/{link}")
        
        # Insertar los datos en la base de datos
        cursor.execute("""
        INSERT INTO scraped_data (titulo, objeto, url)
        VALUES (%s, %s, %s)
        """, (Titulo, objeto, f"https://etb.com/Corporativo/{link}"))

    # Confirmar los cambios en la base de datos
    db.commit()

    # Cerrar la conexión a la base de datos
    cursor.close()
    db.close()
else:
    print(f"Error al acceder a la página. Código de estado: {response.status_code}")
