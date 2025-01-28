import mysql.connector
import json

# Conectar a la base de datos MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="webscraping"
)

cursor = db.cursor()

# Obtener los datos de la tabla
cursor.execute("SELECT titulo, objeto, url FROM scraped_data")
rows = cursor.fetchall()

# Generar el contenido JSON
data = []
for row in rows:
    data.append({
        "titulo": row[0],
        "objeto": row[1],
        "url": row[2]
    })

# Guardar el contenido JSON en un archivo
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

# Cerrar la conexión a la base de datos
cursor.close()
db.close()
