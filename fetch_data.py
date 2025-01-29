import pymysql
import json

def create_json():
    try:
        print("Conectando al servidor MySQL con pymysql...")
        db = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='webscraping'
        )
        print("Conexión exitosa")
        cursor = db.cursor()

        # Modificar la consulta SQL para filtrar registros no deseados
        cursor.execute("""
            SELECT titulo, objeto, url, fecha_creacion 
            FROM scraped_data 
            WHERE objeto != 'Objeto:' 
            AND objeto IS NOT NULL 
            AND LENGTH(TRIM(objeto)) > 10
        """)
        rows = cursor.fetchall()

        # Crear JSON
        data = []
        for row in rows:
            data.append({
                "titulo": row[0],
                "objeto": row[1],
                "url": row[2],
                "fecha": row[3].strftime('%Y-%m-%d %H:%M:%S')
            })

        # Guardar el contenido JSON en un archivo
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            
        print(f"JSON creado con {len(data)} registros")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db' in locals():
            cursor.close()
            db.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    create_json()
