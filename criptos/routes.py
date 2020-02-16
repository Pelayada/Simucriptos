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
    consulta = '''SELECT Movements.id, Movements.date, Movements.time,
                CriptosFrom.symbol, Movements.from_quantity, CriptosTo.symbol, Movements.to_quantity FROM Movements 
                INNER JOIN Criptos as CriptosFrom ON Movements.from_currency = CriptosFrom.id
                INNER JOIN Criptos as CriptosTo ON Movements.to_currency = CriptosTo.id;'''
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
    conn.close()
    return filas

def selectChoices(cursor):
    consulta = """
        SELECT id, symbol, name FROM Criptos;
    """
    coins = cursor.execute(consulta)
    mychoices = [(-1, 'Seleccione Moneda')]
    for e in coins:
        mychoices = mychoices + [(e[0],'{} - {}'.format(e[1], e[2]))]

    return mychoices


def sumaFromCoin(cur, coins):
    dictFromCoin = {}
    for i in coins:
        consulta1 = ''' SELECT from_quantity FROM Movements WHERE from_currency = ? '''
        cur.execute(consulta1,(i[0],))
        rowsFromCoin = cur.fetchall()
        sumaFromCoin = 0
        
        for row in rowsFromCoin:
            sumaFromCoin = sumaFromCoin + row[0]
        dictFromCoin[i[0]] = sumaFromCoin
    return dictFromCoin
    


def sumaToCoin(cur, coins):
    dictToCoin = {}
    for i in coins:
        consulta2 = '''SELECT to_quantity FROM Movements WHERE to_currency = ?'''
        cur.execute(consulta2,(i[0],))
        rowsToCoin = cur.fetchall()
        sumaToCoin = 0
        
        for row in rowsToCoin:
            sumaToCoin = sumaToCoin + row[0]
        dictToCoin[i[0]] = sumaToCoin
    return dictToCoin


def sumaTotalCoin(dictFromCoin, dictToCoin):
    dictTotalCoin = {}
    for i in dictFromCoin:
        restaToFrom = 0
        for j in dictToCoin:
            if i == j:
                restaToFrom = dictToCoin[j] - dictFromCoin[i]
                if i != 2790:
                    dictTotalCoin[i] = round(restaToFrom, 4)
                else:
                    dictTotalCoin[i] = (restaToFrom)*(-1)
    return dictTotalCoin

def converCoin(dictTotalCoin, i, listConverCoin):

    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    parameters = {
        'amount': dictTotalCoin[i],
        'id': i,
        'convert': 'EUR'
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
        changeCoin = data['data']['quote']['EUR']['price']
        listConverCoin.append(changeCoin)
        return listConverCoin

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return e

def updateCoins():
    conn = sqlite3.connect(BASE_DATOS)
    cur = conn.cursor()

    consulta = """
        SELECT id FROM Criptos;
    """
    cur.execute(consulta)
    coins = cur.fetchall()

    listConverCoin = []
    sumaValorActual = 0
    sumaInversion = 0
    sumaFinal = []

    dictFromCoin = sumaFromCoin(cur, coins)
    dictToCoin = sumaToCoin(cur, coins)
    dictTotalCoin = sumaTotalCoin(dictFromCoin, dictToCoin)

    for i in dictTotalCoin:
        if i != 2790:
            converCoin(dictTotalCoin, i, listConverCoin)
        else:
            sumaInversion = dictTotalCoin[i]
            sumaFinal.append(sumaInversion)
    
    for i in listConverCoin:
        sumaValorActual = round((sumaValorActual + i), 4)

    sumaFinal.append(sumaValorActual)

    conn.close()

    return sumaFinal

@app.route("/")
def index():
    registros = todosMovDB()
    return render_template("index.html", registros=registros, route="index")


@app.route("/purchase", methods=('GET', 'POST'))
def purchase():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    
    mychoices = selectChoices(cursor)

    form = SimuForm(request.form)
    form.updateChoices(mychoices)
    
    if request.method == 'GET':
        return render_template('purchase.html', form=form, mychoices=mychoices, route="purchase")

    if form.validate():
        to = request.values.get('to')

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

                    froM = request.values.get('froM')
                    QFrom = request.values.get('QFrom')
                    QTo = request.values.get('QTo') 
                    x = datetime.datetime.now()
                    y = datetime.datetime.now()
                    date = x.strftime('%d-%m-%Y')
                    time = y.strftime('%X')

                    consulta = '''
                        INSERT INTO Movements (date, time, from_currency, from_quantity, to_currency, to_quantity) 
                        VALUES (?,?,?,?,?,?);
                    ''' 
                    cursor.execute(consulta, (date, time, froM, QFrom, idCoin, QTo))
                    conn.commit()
                    conn.close()
                    return redirect(url_for("index"))


            
            consultaCoin = '''
                INSERT INTO Criptos (id, symbol, name) 
                VALUES (?,?,?);
            '''
            cursor.execute(consultaCoin, (idCoin, to, nameCoin))
            
            froM = request.values.get('froM')
            QFrom = request.values.get('QFrom')
            QTo = request.values.get('QTo') 
            x = datetime.datetime.now()
            y = datetime.datetime.now()
            date = x.strftime('%d-%m-%Y')
            time = y.strftime('%X')

            consulta = '''
                INSERT INTO Movements (date, time, from_currency, from_quantity, to_currency, to_quantity) 
                VALUES (?,?,?,?,?,?);
            ''' 
            cursor.execute(consulta, (date, time, froM, QFrom, idCoin, QTo))
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
    
    sumaFinal = updateCoins()
   
    return render_template("status.html", form=form, route='status', sumaFinal=sumaFinal)

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

    