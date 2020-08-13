from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from werkzeug.datastructures import MultiDict
from flask import Markup

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class SignUpForm(FlaskForm):
    email = EmailField('Correo', validators=[DataRequired(), Email("Ingrese su correo electronico")])
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm = PasswordField('Repita su contraseña', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class Todoform(FlaskForm):
    title = StringField('Titulo', validators=[DataRequired()])
    description = StringField('Descripción', validators=[DataRequired()])
    priority = SelectField("Prioridad",choices=[("Baja","Baja"),("Media","Media"),("Alta","Alta"),("Urgente","Urgente")]     )
    deadline = DateField('Plazo', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Crear')

class EditTodoForm(FlaskForm):
    title = StringField('Titulo', validators=[DataRequired()])
    description = StringField('Descripción', validators=[DataRequired()])
    priority = SelectField("Prioridad",choices=[("Baja","Baja"),("Media","Media"),("Alta","Alta"),("Urgente","Urgente")])
    deadline = DateField('Plazo', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField("Estado",choices=[("To Do","To Do"),("Doing","Doing"),("Done","Done")])
    todo_id = HiddenField()
    submit = SubmitField("Guardar Cambios")

class DeleteTodoForm(FlaskForm):
    todo_id = HiddenField()
    submit = SubmitField("Eliminar")


