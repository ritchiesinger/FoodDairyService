from models import db
from main_app import create_app
from config import config

create_result = create_app(config.get("development"), db)
db = create_result.get("db")
app = create_result.get("app")
with app.app_context():
    db.create_all()
