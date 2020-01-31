from criptos import app
from flask import render_template, request, redirect, url_for
import sqlite3
from criptos.forms import SimuForm
import time
import datetime

BASE_DATOS = './data/mov.db'

def todosMovDB():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = 'SELECT id, date, unix, from_currency, from_quantity, to_currency, to_quantity, precio_unitario FROM Movements;'
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
            
    conn.close()
    return filas
    

@app.route("/")
def index():
    registros = todosMovDB()

    return render_template("index.html", registros=registros)


@app.route("/purchase", methods=('GET', 'POST'))
def purchase():
    form = SimuForm(request.form)

    if request.method == 'GET':
        return render_template('purchase.html', form=form)

    froM = request.values.get('froM')
    to = request.values.get('to')
    QFrom = request.values.get('QFrom')
    QTo = request.values.get('QTo')
    QPU = request.values.get('QPU')

    x = datetime.datetime.now()
    y = datetime.datetime.now()

    date = x.strftime('%x')
    unix = y.strftime('%X')



    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = '''
        INSERT INTO Movements (date, unix, from_currency, from_quantity, to_currency, to_quantity, precio_unitario) 
        VALUES (?,?,?,?,?,?,?);
    ''' 
    cursor.execute(consulta, (date, unix, froM, QFrom, to, QTo, QPU))
    conn.commit()
    conn.close()

    
    return redirect(url_for("index"))


@app.route("/status")
def status():
    
    return render_template("status.html")
