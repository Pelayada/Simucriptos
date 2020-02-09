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
    print("SimuForm")
    froM = SelectField('From', choices = [('EUR', 'EUR'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('XRP', 'XRP'), ('LTC', 'LTC'), ('BCH', 'BCH'), ('BNB', 'BNB'), ('USDT', 'USDT'), ('EOS', 'EOS'), ('BSV', 'BSV'), ('XLM', 'XLM'), ('ADA', 'ADA'), ('TRX', 'TRX')] )
    to = SelectField('To', choices = [('EUR', 'EUR'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('XRP', 'XRP'), ('LTC', 'LTC'), ('BCH', 'BCH'), ('BNB', 'BNB'), ('USDT', 'USDT'), ('EOS', 'EOS'), ('BSV', 'BSV'), ('XLM', 'XLM'), ('ADA', 'ADA'), ('TRX', 'TRX')] )
    QFrom = StringField('QFrom', validators = [InputRequired(), validate_number])
    QTo = StringField('QTo')
    QPU = StringField('QPU')

    submit = SubmitField('Ok')

    