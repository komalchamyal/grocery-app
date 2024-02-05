from flask import Flask
from flask_cors import CORS
from model import db
import os
from flask_jwt_extended import JWTManager
from workers import make_celery

curr_dir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

CORS(app)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/1'
)
celery = make_celery(app)

# celery.conf.update(broker_url="redis://127.0.0.1:6379/0", result_backend="redis://127.0.0.1:6379/2")
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(curr_dir,"database.sqlite3?charset=utf8")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='196543'


db.init_app(app)
app.app_context().push()
app.config['JWT_SECRET_KEY'] = '552739'

# celery.Task= ContextTask
jwt = JWTManager(app)

from controllers import *

if __name__=="__main__":
    app.run(debug=True, port=5000)