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

# Selección de elementos de tabla Movements para route index.
def todosMovDB():
    conn = sqlite3.connect(BASE_DATOS)
    cur = conn.cursor()
    consulta = '''SELECT Movements.id, Movements.date, Movements.time,
                CriptosFrom.symbol, Movements.from_quantity, CriptosTo.symbol, Movements.to_quantity FROM Movements 
                INNER JOIN Criptos as CriptosFrom ON Movements.from_currency = CriptosFrom.id
                INNER JOIN Criptos as CriptosTo ON Movements.to_currency = CriptosTo.id;'''
    rows = cur.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
    conn.close()
    return filas

# Selección de elementos de tabla Criptos para select dinámico.
def selectChoices(cursor):
    consulta = """
        SELECT id, symbol, name FROM Criptos;
    """
    coins = cursor.execute(consulta)
    mychoices = [(-1, 'Seleccione Moneda')]
    for e in coins:
        mychoices = mychoices + [(e[0],'{} - {}'.format(e[1], e[2]))]

    return mychoices

# Descartar posibles fallos entre monedas.
def errorCoins(dictTotalCoin, idCoin, form):
    froM = int(request.values.get('froM'))
    QFrom = float(request.values.get('QFrom'))
    for j in dictTotalCoin:
        if froM != idCoin:
            if froM == j and froM != 2790:
                if QFrom > dictTotalCoin[j]:
                    error = "No tiene suficiente saldo de esa moneda."
                    return error
        else:
            error = "Las monedas no pueden ser iguales."
            return error
            
# Introducir elementos en la tabla Criptos.
def consultCoin(cur, idCoin, to, nameCoin):
    consultaCoin = '''
        INSERT INTO Criptos (id, symbol, name) 
        VALUES (?,?,?);
    '''
    try:
        cur.execute(consultaCoin, (idCoin, to, nameCoin))
    except (sqlite3.Error, Exception) as e:
        print("Error en consultCoin - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('purchase.html', form=form, route='purchase', textError=textError)

# Introducir elementos en la tabla Movements.
def insertMovements(conn, cur, idCoin):
    froM = int(request.values.get('froM'))
    QFrom = float(request.values.get('QFrom'))

    QTo = request.values.get('QTo') 
    x = datetime.datetime.now()
    y = datetime.datetime.now()
    date = x.strftime('%d-%m-%Y')
    time = y.strftime('%X')

    consulta = '''
        INSERT INTO Movements (date, time, from_currency, from_quantity, to_currency, to_quantity) 
        VALUES (?,?,?,?,?,?);
    ''' 

    try:
        cur.execute(consulta, (date, time, froM, QFrom, idCoin, QTo))

    except (sqlite3.Error, Exception) as e:
        print("Error en insertMovements - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('purchase.html', form=form, route='purchase', textError=textError)

# Sumatorio de la columna from_quantity.       
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

# Sumatorio de la columna to_quantity.       
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

# Diferencia entre to_quantity y from_quantity.
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

# Conversión de monedas para la suma de valor actual.
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
        print("Error en API ConverCoin - BBDD", e)
        textError = "Fallo en API. Inténtelo más tarde."
        return render_template('status.html', form=form, route='purchase', textError=textError)

# Valor invertido y valor actual de la route status.
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
    try:
        registros = todosMovDB()
        return render_template("index.html", registros=registros, route="index")

    except (sqlite3.Error, Exception) as e:
        print("Error en index - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('index.html', route='index', textError=textError)

@app.route("/purchase", methods=('GET', 'POST'))
def purchase():
    try:
        conn = sqlite3.connect(BASE_DATOS)
        cur = conn.cursor()
        
        mychoices = selectChoices(cur)
        form = SimuForm(request.form)
        form.updateChoices(mychoices)

        consulta = """
            SELECT id FROM Criptos;
        """
        cur.execute(consulta)

        coins = cur.fetchall()

        dictFromCoin = sumaFromCoin(cur, coins)
        dictToCoin = sumaToCoin(cur, coins)

    except (sqlite3.Error, Exception) as e:
        print("Error en purchase - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('purchase.html', form=form, route='purchase', textError=textError) 

    dictTotalCoin = sumaTotalCoin(dictFromCoin, dictToCoin)

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
            if to != 'EUR':
                idCoin = data['data'][0]['id']
                nameCoin = data['data'][0]['name']
            else:
                idCoin = 2790
                nameCoin = 'Euro'

            # Comprueba si la moneda ya ha sido guardada en la tabla Criptos,
            # para no actualizar el select from.
            
            for i in range(len(mychoices)):
                if idCoin == mychoices[i][0]:

                    # Comprueba si tiene saldo suficiente y si las monedas usadas
                    # son distintas entre ellas.
                    textError = errorCoins(dictTotalCoin, idCoin, form)
                    if textError:
                        form.QFrom.data = ''
                        form.QTo.data = ''
                        form.froM.data = '-1'
                        form.to.data = '-1'
                        return render_template('purchase.html', form=form, route='purchase', textError=textError)
                    
                    insertMovements(conn, cur, idCoin)
                    conn.commit()
                    conn.close()
                    return redirect(url_for("index"))
            
            consultCoin(cur, idCoin, to, nameCoin)

            # Comprueba si tiene saldo suficiente y si las monedas usadas
            # son distintas entre ellas.
            textError = errorCoins(dictTotalCoin, idCoin, form)
            if textError:
                return render_template('purchase.html', form=form, route='purchase', textError=textError)            
            insertMovements(conn, cur, idCoin)
            conn.commit()   
            conn.close()

            return redirect(url_for("index"))

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print("Error en API - purchase", e)
            textError = "Fallo en API. Inténtelo más tarde."
            return render_template('purchase.html', form=form, route='purchase', textError=textError)     
    else:
        return render_template('purchase.html', form=form, route='purchase')

@app.route("/status", methods=('GET', 'POST'))
def status():
    form = SimuForm(request.form)
    try:
        sumaFinal = updateCoins()

    except (sqlite3.Error, Exception) as e:
        print("Error en status - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('status.html', form=form, route='purchase', textError=textError) 
   
    return render_template("status.html", form=form, route='status', sumaFinal=sumaFinal)

@app.route("/coin")
@cross_origin()
def coin():
    try:
        conn = sqlite3.connect(BASE_DATOS)
        cur = conn.cursor()

        mychoices = selectChoices(cur)
        form = SimuForm(request.form)
        form.updateChoices(mychoices)
        
        froM = request.values.get('symbol')
        to = request.values.get('convert')
        QFrom = request.values.get('amount')

        cursor = cur.execute("SELECT symbol FROM Criptos WHERE id=?", (froM,))
    
    except (sqlite3.Error, Exception) as e:
        print("Error en API Coin - BBDD", e)
        textError = "Fallo en Base de Datos. Inténtelo más tarde."
        return render_template('purchase.html', form=form, route='purchase', textError=textError) 

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
        data = json.loads(response.text)
        if data['status']['error_code'] == 0:
            return data
        else:
            raise Exception
        
    except (ConnectionError, Timeout, TooManyRedirects, Exception) as e:
        print("Error en API Coin", e)
        textError = "Fallo en API. Inténtelo más tarde."
        return textError, 400
    