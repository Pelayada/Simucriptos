# Simucriptos
Aplicación web en Flask, cuya funcionalidad es simular la conversión e inversión de Criptomonedas.

Se podría ver un ejemplo en la IP:  http://3.136.37.62/

## Descarga
```
git clone https://github.com/Pelayada/Simucriptos.git
```

## Requisitos
Copiar el contenido de config_template.py a un nuevo archivo, el cual deberá llamarse config.py.
Modificar __SECRET_KEY__ y __API_KEY__. Para la primera podrá introducir cualquier cadena de caracteres. En la segunda, deberá escribir la adquirida en la api de coinmarketcap. Para ello, valdrá con crearse una cuenta básica en __https://coinmarketcap.com/api__

## Instalación
* Instalar entorno virtual
```
python -m venv <nombre-entorno-virtual>
```
* Activar de entorno virtual
```
Mac: source <nombre-entorno-virtual>/bin/activate
Linux: source <nombre-entorno-virtual>/bin/activate
Windows: <nombre-entorno-virtual>\Scripts\activate

```
* Instalar dependencias
```
pip install -r requirements.txt
```
* Exportar flask variable
```
export FLASK_APP=run.py
```

## Ejecución

```
flask run
```
