from flask_migrate import Migrate, MigrateCommand
from main_app import create_app
from config import config
from models import db
from flask_script import Manager


app = create_app(config.get("development"), db)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
