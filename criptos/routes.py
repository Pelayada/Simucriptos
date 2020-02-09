from criptos import app
from flask import render_template, request, redirect, url_for
import sqlite3
from criptos.forms import SimuForm
import time
import datetime
import json
import requests
from flask_cors import CORS, cross_origin
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

BASE_DATOS = './data/mov.db'

def todosMovDB():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = 'SELECT id, date, unix, from_currency, from_quantity, to_currency, to_quantity FROM Movements;'
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
    
    conn.close()
    return filas
    

@app.route("/")
def index():
    registros = todosMovDB()
    print("registros", registros)
    return render_template("index.html", registros=registros)


@app.route("/purchase", methods=('GET', 'POST'))
def purchase():
    form = SimuForm(request.form)

    if request.method == 'GET':
        return render_template('purchase.html', form=form)

    if form.validate():
        froM = request.values.get('froM')
        to = request.values.get('to')
        QFrom = request.values.get('QFrom')
        QTo = request.values.get('QTo')
        

        x = datetime.datetime.now()
        y = datetime.datetime.now()
        date = x.strftime('%x')
        unix = y.strftime('%X')

        conn = sqlite3.connect(BASE_DATOS)
        cursor = conn.cursor()
        consulta = '''
            INSERT INTO Movements (date, unix, from_currency, from_quantity, to_currency, to_quantity) 
            VALUES (?,?,?,?,?,?);
        ''' 
        cursor.execute(consulta, (date, unix, froM, QFrom, to, QTo))
        conn.commit()
        conn.close()

    
        return redirect(url_for("index"))
    else:
        return render_template('purchase.html', form=form)


@app.route("/status")
def status():
    
    return render_template("status.html")

@app.route("/coin")
@cross_origin()
def coin():
    froM = request.values.get('symbol')
    to = request.values.get('convert')
    QFrom = request.values.get('amount')
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    parameters = {
    'amount': QFrom,
    'symbol': froM,
    'convert': to
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '2ddda9f5-57bc-4f94-8cbf-7c5632d4e1c7',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = response.text
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return e

    