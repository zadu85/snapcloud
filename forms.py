from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User
from flask_wtf.file import FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    username = StringField('Nume de utilizator', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Adresa de email', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[DataRequired()])
    confirm_password = PasswordField('Confirma parola', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Inregistreaza-te')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Acest nume de utilizator este deja folosit. Alege altul.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Acest email este deja inregistrat. Conecteaza-te sau foloseste alt email.')

class LoginForm(FlaskForm):
    email = StringField('Adresa de email', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[DataRequired()])
    remember = BooleanField('Tine-ma minte')
    submit = SubmitField('Autentificare')

class AlbumForm(FlaskForm):
    name = StringField('Nume Album', validators=[DataRequired()])
    is_private = BooleanField('Album Privat', default=True)
    submit = SubmitField('Creeaza Album')


class PhotoUploadForm(FlaskForm):
    photo = FileField('Alege fotografia', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Doar imaginile sunt permise!')])
    submit = SubmitField('Incarcare')

class ShareLinkForm(FlaskForm):
    submit = SubmitField('Genereaza Link de Partajare')
