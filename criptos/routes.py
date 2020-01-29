from criptos import app
from flask import render_template
import sqlite3

BASE_DATOS = './data/mov.db'

def todosMovDB():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = 'SELECT id, date, time, from_currency, from_quantity, to_currency, to_quantity FROM Movements'
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
        print(filas)
    
    return filas


@app.route("/")
def index():
    registros = todosMovDB()

    return render_template("index.html", registros=registros)


@app.route("/purchase")
def purchase():

    return render_template("purchase.html")


@app.route("/status")
def status():

    return render_template("status.html")

