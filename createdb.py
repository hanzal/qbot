from app import app
from models import db
import urllib2
import json
db.init_app(app)

with app.app_context():
	from app import History
	db.create_all()
