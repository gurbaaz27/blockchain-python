from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class TransactionForm(FlaskForm):
    sender       =   StringField("Sender", validators=[DataRequired()])
    recipient    =   StringField("Recipient", validators=[DataRequired()])
    amount       =   StringField("Amount", validators=[DataRequired()])
    submit      =    SubmitField("Submit")

class NodeRegisterForm(FlaskForm):
    node               =   StringField("Node Address", validators=[DataRequired()])
    submit             =   SubmitField("Register Node")