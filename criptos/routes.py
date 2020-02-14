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
API_KEY = app.config['API_KEY']

def todosMovDB():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = 'SELECT id, date, time, from_currency, from_quantity, to_currency, to_quantity FROM Movements;'
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
    
    conn.close()
    return filas
    

@app.route("/")
def index():
    registros = todosMovDB()
    return render_template("index.html", registros=registros, route="index")


@app.route("/purchase", methods=('GET', 'POST'))
def purchase():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = """
        SELECT id, symbol, name FROM Criptos;
    """
    coins = cursor.execute(consulta)
    mychoices = [(-1, 'Seleccione Moneda')]
    for e in coins:
        mychoices = mychoices + [(e[1], e[1])]
    form = SimuForm(request.form)
    form.updateChoices(mychoices)
    
    if request.method == 'GET':
        return render_template('purchase.html', form=form, mychoices=mychoices, route="purchase")

    if form.validate():
        froM = request.values.get('froM')
        to = request.values.get('to')
        QFrom = request.values.get('QFrom')
        QTo = request.values.get('QTo') 
        x = datetime.datetime.now()
        y = datetime.datetime.now()
        date = x.strftime('%x')
        time = y.strftime('%X')

        conn = sqlite3.connect(BASE_DATOS)
        cursor = conn.cursor()
        consulta = '''
            INSERT INTO Movements (date, time, from_currency, from_quantity, to_currency, to_quantity) 
            VALUES (?,?,?,?,?,?);
        ''' 
        cursor.execute(consulta, (date, time, froM, QFrom, to, QTo))

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
        parameters = {
        'symbol': to,
        }
        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
        }
        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            idCoin = data['data'][0]['id']
            nameCoin = data['data'][0]['name']

            for i in range(len(mychoices)):
                if idCoin == mychoices[i][0]: 
                    conn.commit()
                    conn.close()
                    return redirect(url_for("index"))
            
            consultaCoin = '''
                INSERT INTO Criptos (id, symbol, name) 
                VALUES (?,?,?);
            '''
            cursor.execute(consultaCoin, (idCoin, to, nameCoin))
            conn.commit()
            conn.close()

            return redirect(url_for("index"))
        
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return(e)

         
    else:
        return render_template('purchase.html', form=form, route=purchase)


@app.route("/status", methods=('GET', 'POST'))
def status():
    form = SimuForm(request.form)

    conn = sqlite3.connect(BASE_DATOS)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Movements WHERE from_currency='EUR'")
 
    rows = cur.fetchall()
    sumaInvertido = 0

    for row in rows:
        sumaInvertido = sumaInvertido + row[4]

    conn.close()

    conn = sqlite3.connect(BASE_DATOS)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Movements WHERE from_currency='BTC'")
 
    rows = cur.fetchall()
    sumaValorActual = 0

    for row in rows:
        sumaValorActual = sumaValorActual + row[4]

    conn.close()
   

    
    return render_template("status.html", sumaInvertido=sumaInvertido,sumaValorActual=sumaValorActual, form=form, route='status')

@app.route("/coin")
@cross_origin()
def coin():
    form = SimuForm(request.form)
    
    froM = request.values.get('symbol')
    to = request.values.get('convert')
    QFrom = request.values.get('amount')

    conn = sqlite3.connect(BASE_DATOS)
    cur = conn.cursor()
    cursor = cur.execute("SELECT symbol FROM Criptos WHERE id=?", (froM,))
    fromSymbol = cursor.fetchone()
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    parameters = {
    'amount': QFrom,
    'symbol': fromSymbol,
    'convert': to
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = response.text
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return e

    