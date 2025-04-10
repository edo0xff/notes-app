import sqlite3
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()
conexion = sqlite3.connect("notas.db")

try:
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    contenido TEXT,
                    fecha TIMESTAMP
        )
        """)
except sqlite3.OperationalError:
    print("Hubo un error")

conexion.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/notas")
def read_notas(search_query: str = None):
    conexion = sqlite3.connect("notas.db")
    cursor = conexion.cursor()
    if search_query:
        cursor.execute(
            "SELECT id, title, contenido, fecha FROM notas WHERE title LIKE ? OR contenido LIKE ?",
            (f"%{search_query}%", f"%{search_query}%"),
        )
    else:
        cursor.execute("SELECT id, title, contenido, fecha FROM notas")
    notas = cursor.fetchall()
    conexion.close()
    return {"notas": [row for row in notas]}


@app.post("/nota")
def create_nota(title: str, contenido: str):
    fecha = datetime.now().isoformat()  # Generate the current timestamp
    conexion = sqlite3.connect("notas.db")
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO notas (title, contenido, fecha) VALUES (?, ?, ?)",
        (title, contenido, fecha),
    )
    conexion.commit()
    new_id = cursor.lastrowid
    conexion.close()
    return {"id": new_id, "title": title, "contenido": contenido, "fecha": fecha}


@app.put("/nota/{nota_id}")
def update_nota(nota_id: int, title: str, contenido: str):
    fecha = datetime.now().isoformat()  # Generate the current timestamp
    conexion = sqlite3.connect("notas.db")
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE notas SET title = ?, contenido = ?, fecha = ? WHERE id = ?",
        (title, contenido, fecha, nota_id),
    )
    conexion.commit()
    updated_rows = cursor.rowcount
    conexion.close()
    if updated_rows == 0:
        return {"error": "Nota not found"}
    return {"id": nota_id, "title": title, "contenido": contenido, "fecha": fecha}


@app.delete("/nota/{nota_id}")
def delete_nota(nota_id: int):
    conexion = sqlite3.connect("notas.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM notas WHERE id = ?", (nota_id,))
    conexion.commit()
    deleted_rows = cursor.rowcount
    conexion.close()
    if deleted_rows == 0:
        return {"error": "Nota not found"}
    return {"message": "Nota deleted successfully", "id": nota_id}