from models import db
from main_app import create_app
from config import config
from socket import gethostname

if 'liveconsole' in gethostname():
    create_result = create_app(config.get("production"), db)
else:
    create_result = create_app(config.get("development"), db)
db = create_result.get("db")
app = create_result.get("app")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()