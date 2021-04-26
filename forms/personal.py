from flask_wtf import FlaskForm
from wtforms import FileField, TextField, SubmitField
from wtforms.validators import DataRequired


class PersonalForm(FlaskForm):
    icon = FileField(validators=[DataRequired()])
    body = TextField(validators=[DataRequired()])
    submit = SubmitField('Сохранить')