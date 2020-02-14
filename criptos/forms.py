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
    froM = SelectField('From', coerce=int)
    to = SelectField('To', choices = [(-1, 'Seleccione Moneda'), ('EUR', 'EUR - Euro'), ('BTC', 'BTC - Bitcoin'), ('ETH', 'ETH - Ethereum'), ('XRP', 'XRP - XRP'), ('LTC', 'LTC - Litcoin'), ('BCH', 'BCH - Bitcoin cash'), ('BNB', 'BNB - Binance coin'), ('USDT', 'USDT - Tether'), ('EOS', 'EOS - EOS'), ('BSV', 'BSV - Bitcoin SV'), ('XLM', 'XLM - Stellar'), ('ADA', 'ADA - Cardano'), ('TRX', 'TRX - Tron')])
    QFrom = StringField('QFrom', validators = [InputRequired(), validate_number])
    QTo = StringField('QTo')
    QPU = StringField('QPU', render_kw={'disabled':''})
    submit = SubmitField('Ok')

    def updateChoices(self, mychoices):
        self.froM.choices = mychoices

    
    invertido = StringField('invertido', render_kw={'disabled':''})
    valorActual = StringField('valorActual', render_kw={'disabled':''})





    