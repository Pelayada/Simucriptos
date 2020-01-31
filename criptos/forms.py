from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, HiddenField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, ValidationError, AnyOf, Email
from wtforms.widgets import TextArea, Select

class SimuForm(FlaskForm):
    froM = SelectField('From', choices = [('EUR', 'EUR'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('XRP', 'XRP'), ('LTC', 'LTC'), ('BCH', 'BCH'), ('BNB', 'BNB'), ('USDT', 'USDT'), ('EOS', 'EOS'), ('BSV', 'BSV'), ('XLM', 'XLM'), ('ADA', 'ADA'), ('TRX', 'TRX')] )
    to = SelectField('To', choices = [('EUR', 'EUR'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('XRP', 'XRP'), ('LTC', 'LTC'), ('BCH', 'BCH'), ('BNB', 'BNB'), ('USDT', 'USDT'), ('EOS', 'EOS'), ('BSV', 'BSV'), ('XLM', 'XLM'), ('ADA', 'ADA'), ('TRX', 'TRX') )
    QFrom = DecimalField('QFrom', validators = [DataRequired()])
    QTo = DecimalField('QTo', validators = [DataRequired()])
    QPU = DecimalField('QPU', validators = [DataRequired()])

    submit = SubmitField('Ok')