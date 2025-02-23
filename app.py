from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect  # Importă CSRFProtect


app = Flask(__name__)
app.config.from_object(Config)
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)  # Inițializează protecția CSRF

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
