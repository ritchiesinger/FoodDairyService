from models import db
from main_app import create_app
from config import Config
from socket import gethostname

create_result = create_app(Config(), db)
db = create_result.get("db")
app = create_result.get("app")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
