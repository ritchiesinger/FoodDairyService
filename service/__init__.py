from flask import Flask, render_template
from .models import db
from flask_migrate import Migrate

migrate = Migrate()


def create_app(test_config=None):
    # Создаём и настраиваем приложение
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ritchie_singer:qwerty@localhost/fooddairy'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)

    if test_config is None:
        # Загружаем настройки из файла конфигураций если не переданы явно тестовые настройки
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Загружаем тестовые настройки которые переданы явно
        app.config.from_mapping(test_config)

    from . import routes
    app.register_blueprint(routes.bp)

    @app.errorhandler(404)
    def fallback_to_react(e):
        print(f"Указанный маршрут не определён на сервере ({e}). Переадресуем на маршрутизатор ReactJS")
        return render_template('index.html')

    return app
