import requests
from bs4 import BeautifulSoup
import mysql.connector

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
    db = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_base_datos"
    )

    cursor = db.cursor()

    # Crear la tabla si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(255),
        objeto TEXT,
        url TEXT
    )
    """)

    for contenedor in contenedores:
        # Buscar todas las etiquetas <p> dentro del contenedor
        Titulo = contenedor.find("h4").text.strip() if contenedor.find("h4") else "No encontrado"
        print(f"Titulo: {Titulo}")
        parrafos = contenedor.find_all("p")
        for i, parrafo in enumerate(parrafos[:2]):
            # Obtener el texto de cada etiqueta <p>
            objeto = parrafo.text.strip()
            
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
