from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, HiddenField, SelectField, DecimalField, IntegerField   
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError, AnyOf, Email, NumberRange
from wtforms.widgets import TextArea, Select

def validate_number(form, field):
    try:
        float(field.data)
    except ValueError:
        raise ValidationError('Tiene que ser un número valido.')

class SimuForm(FlaskForm):
    froM = SelectField('From', choices = [('EUR', 'EUR - EURO'), ('BTC', 'BTC - BITCOIN'), ('ETH', 'ETH - ETHEREUM'), ('XRP', 'XRP - XRP'), ('LTC', 'LTC - LITCOIN'), ('BCH', 'BCH - BITCOIN CASH'), ('BNB', 'BNB - BINANCE COIN'), ('USDT', 'USDT - TETHER'), ('EOS', 'EOS - EOS'), ('BSV', 'BSV - BITCOIN SV'), ('XLM', 'XLM - STELLAR'), ('ADA', 'ADA - CARDANO'), ('TRX', 'TRX - TRON')] )
    to = SelectField('To', choices = [('EUR', 'EUR - EURO'), ('BTC', 'BTC - BITCOIN'), ('ETH', 'ETH - ETHEREUM'), ('XRP', 'XRP - XRP'), ('LTC', 'LTC - LITCOIN'), ('BCH', 'BCH - BITCOIN CASH'), ('BNB', 'BNB - BINANCE COIN'), ('USDT', 'USDT - TETHER'), ('EOS', 'EOS - EOS'), ('BSV', 'BSV - BITCOIN SV'), ('XLM', 'XLM - STELLAR'), ('ADA', 'ADA - CARDANO'), ('TRX', 'TRX - TRON')] )
    QFrom = StringField('QFrom', validators = [InputRequired(), validate_number])
    QTo = StringField('QTo')
    QPU = StringField('QPU', render_kw={'disabled':''})
    submit = SubmitField('Ok')

    invertido = StringField('invertido', render_kw={'disabled':''})
    valorActual = StringField('valorActual', render_kw={'disabled':''})




    