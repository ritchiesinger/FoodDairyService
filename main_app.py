from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import json
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail, Message
import random
from config import config

auth = HTTPBasicAuth()
app = Flask(__name__)
app.config.from_object(config.get("development"))
mail = Mail(app)
db = SQLAlchemy(app)


def password_generator():
    avaliable_symbols = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    password_lenght = 8
    generated_password = "".join(random.sample(avaliable_symbols, password_lenght))
    return generated_password


def send_mail(recipients, subject, html):
    msg = Message(subject=subject, recipients=recipients, html=html)
    with app.app_context():
        mail.send(msg)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_tokens(self, is_refresh=False, expiration=60):  # 60 секунд на пртухание
        """ Генерация токенов
        :param is_refresh: параметр, определяющий какой токен надо сгенерировать. True - будет сгенерирован
        refresh-токен, False - будет сгенерирован auth-токен. Любое другое значение - будут сгенерированы оба токена.
        :param expiration: время протухания auth токена в секундах. Время протухания refresh токена принимается в 3
        раза больше.
        :return: в зависимости от входящих параметров вернётся либо какой-то один из токенов, либо оба. """
        if is_refresh is False:
            auth_token = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
            result = {"AuthToken": auth_token.dumps({'id': self.id}).decode('ascii')}
        elif is_refresh is True:
            refresh_token = Serializer(app.config['SECRET_KEY'] + "refresh", expires_in=expiration * 3)
            result = {"RefreshToken": refresh_token.dumps({'id': self.id}).decode('ascii')}
        else:
            auth_token = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
            refresh_token = Serializer(app.config['SECRET_KEY'] + "refresh", expires_in=expiration * 3)
            result = {"AuthToken": auth_token.dumps({'id': self.id}).decode('ascii'),
                      "RefreshToken": refresh_token.dumps({'id': self.id}).decode('ascii')}
        return result

    @staticmethod
    def verify_auth_token(auth_token, refresh_token):
        auth_token_check = Serializer(app.config['SECRET_KEY'])
        return_dict = dict()
        try:
            data = auth_token_check.loads(auth_token)
            user = User.query.get(data['id'])
            return_dict.update({"User": user})
            try_refresh_token = user.verify_refresh_token(refresh_token)
            if try_refresh_token is None:
                new_tokens = user.generate_tokens(is_refresh=True)
                return_dict.update({"NewTokens": new_tokens})
            return return_dict
        except SignatureExpired:
            # return None  # Токен протух
            try_refresh_token = User.verify_refresh_token(refresh_token)
            if try_refresh_token is not None:
                new_tokens = try_refresh_token.generate_tokens()
                return {"User": try_refresh_token, "NewTokens": new_tokens}
            else:
                return None
        except BadSignature:
            return None  # Неверный токен

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def verify_refresh_token(refresh_token):
        refresh_token_check = Serializer(app.config['SECRET_KEY'] + "refresh")
        try:
            data = refresh_token_check.loads(refresh_token)
        except SignatureExpired:
            return None  # Токен протух
        except BadSignature:
            return None  # Неверный токен
        user = User.query.get(data['id'])
        return user


class Measures(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    measure_name = db.Column(db.String(128), unique=True, nullable=False)
    measure_dimension = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String())

    def __repr__(self):
        return f"<Measures: {self.measure_name}>"


class MeasuresDairyRows(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    measure_datetime = db.Column(db.DateTime, nullable=False)
    measure_id = db.Column(db.Integer, db.ForeignKey('measures.id'), nullable=False)
    value = db.Column(db.REAL, nullable=False)
    user = db.relationship("User", foreign_keys=user_id)
    measure_name = db.relationship("Measures", foreign_keys=measure_id)

    def __repr__(self):
        return f"<MeasuresDairyRows: {self.id}>"


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(128), unique=True, nullable=False)
    callories = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.REAL, nullable=False)
    protein = db.Column(db.REAL, nullable=False)
    carbohydrate = db.Column(db.REAL, nullable=False)
    description = db.Column(db.String())
    image_link = db.Column(db.String())
    disabled = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Products {self.id} ({self.name})>"


class ProductsDairyRows(db.Model):
    __tablename__ = "products_dairy_rows"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    record_datetime = db.Column(db.DateTime, nullable=False)
    product_weight = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", foreign_keys=user_id)
    product = db.relationship("Products", foreign_keys=product_id)

    def __repr__(self):
        return f"<ProductDairyRows {self.id}>"


class Recipes(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_private = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String())
    user = db.relationship("User", foreign_keys=user_id)

    def get_recipe_for_list(self):
        return {"RecipeID": self.id, "RecipeName": self.name, "RecipeOwner": self.user.username,
                "RecipeDescription": self.description, "IsPrivate": self.is_private}

    def get_recipe(self):
        product_list = list()
        recipes_products = RecipesProducts.query.filter(RecipesProducts.recipe_id == self.id).all()
        for product in recipes_products:
            product_list.append(
                {"ProductName": product.product.name, "ProductID": product.product.id,
                 "ProductWeight": product.product_weight,
                 "ProductTotalCallories": round(product.product_weight * product.product.callories / 100, 2),
                 "ProductTotalFat": round(product.product_weight * product.product.fat / 100, 2),
                 "ProductTotalProtein": round(product.product_weight * product.product.protein / 100, 2),
                 "ProductTotalCarbohydrate": round(product.product_weight * product.product.carbohydrate / 100, 2)})
        total_callories = round(sum([product.get("ProductTotalCallories") for product in product_list]), 2)
        total_protein = round(sum([product.get("ProductTotalProtein") for product in product_list]), 2)
        total_fat = round(sum([product.get("ProductTotalFat") for product in product_list]), 2)
        total_carbohydrates = round(sum([product.get("ProductTotalCarbohydrate") for product in product_list]), 2)
        return {"RecipeID": self.id, "RecipeName": self.name, "RecipeOwner": self.user.username,
                "RecipeDescription": self.description, "IsPrivate": self.is_private,
                "RecipeProducts": product_list, "TotalCallories": total_callories, "TotalProtein": total_protein,
                "TotalFat": total_fat, "TotalCarbohydrate": total_carbohydrates}

    def __repr__(self):
        return f"<Recipes {self.name}>"


class RecipesProducts(db.Model):
    __tablename__ = "recipes_products"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_weight = db.Column(db.Integer, nullable=False)
    product = db.relationship("Products", foreign_keys=product_id)
    recipe = db.relationship("Recipes", foreign_keys=recipe_id)

    def __repr__(self):
        return f"<RecipesProducts {self.recipe_id}: {self.product_id}>"


@app.route('/api/Users/', methods=['POST'])
def user_registration():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username in (None, "") or password in (None, ""):
        error_text = "Username or password is not specified!"
        return json.dumps({'Error': error_text}), 400, {'ContentType': 'application/json'}
    elif User.query.filter_by(username=username).first() is not None:
        error_text = f"'{username}' already exist!"
        return json.dumps({'Error': error_text}), 400, {'ContentType': 'application/json'}
    elif User.query.filter_by(email=email).first() is not None:
        error_text = f"'{email}' already exist!"
        return json.dumps({'Error': error_text}), 400, {'ContentType': 'application/json'}
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201


@app.route('/api/GetToken/', methods=['GET'])
@auth.login_required
def get_tokens():
    tokens = g.user.get("User").generate_tokens(is_refresh="All")
    return jsonify({"data": {"AuthToken": tokens.get("AuthToken"), "RefreshToken": tokens.get("RefreshToken")}})


@auth.verify_password
def verify_password(username_or_auth_token, password_or_refresh_token):
    # Сначала пробуем авторизоваться по токену
    user = User.verify_auth_token(auth_token=username_or_auth_token, refresh_token=password_or_refresh_token)
    if not user:
        # А теперь по обычному - логину и паролю
        user = User.query.filter_by(username=username_or_auth_token).first()
        if not user or not user.verify_password(password_or_refresh_token):
            return False
        user = {"User": user}
    g.user = user
    return True


@app.route('/api/PasswordReset/', methods=["GET"])
def password_reset():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return json.dumps({'Error': "User not found!"}), 400, {'ContentType': 'application/json'}
    else:
        new_password = password_generator()
        user.hash_password(new_password)
        db.session.commit()
        html = "<h2>Уважаемый пользователь!</h2>" \
               "<p>Вы получили это письмо, т.к сделали запрос на восстановление пароля в " \
               "сервисе FoodDairy.</p>" \
               f"<p>Пароль к учётной записи {user.email} сброшен и сгенерирован новый, который вы сможете в любой " \
               "момент поменять самостоятельно.<p>" \
               f"<p>Сгенерированный пароль:<b>{new_password}</b></p>"
        send_mail(recipients=["ritchie_singer@mail.ru"], subject="Восстановление пароля к сервису FoodDairy", html=html)
        return jsonify({"data": f"New password send to {email}!"})


@app.route('/api/SetNewPassword/', methods=["POST"])
@auth.login_required
def set_new_password():
    """ Метод установки нового пароля. Требуется авторизация. На вход ожидает JSON вида: {"password": "somepassword"}
    :return: Стандартный контракт вида:  {"data": None, "ErrorCode": 0, "ErrorText": "New password is set!"} """
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    new_password = request.json.get('password')
    user = User.query.filter_by(username=g.user.username).first()
    user.hash_password(new_password)
    db.session.commit()
    return_dict.update({"data": None, "ErrorCode": 0, "ErrorText": "New password is set!"})
    return json.dumps(return_dict), 200, {'ContentType': 'application/json'}


@app.route("/api/GetMyProfile/")
@auth.login_required
def get_my_profile():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    return_dict.update({"data": {"UserName": g.user.username, "Email": g.user.email}})
    return jsonify(return_dict)


@app.route('/api/MeasureValues/', methods=["GET", "POST", "PATCH", "DELETE"])
@auth.login_required
def measure_values():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    if request.method == "GET":  # Получаем данные
        date_format = '%Y%m%d'
        measure_id = request.args.get('measure_id')
        date_interval = request.args.get('date_interval')
        if date_interval:
            try:
                date_interval = date_interval.split("-")
                date_from = datetime.datetime.strptime(date_interval[0], date_format)
                date_to = datetime.datetime.strptime(date_interval[1], date_format)
            except ValueError:
                error_text = "Unexpected date_interval format! Expected 'YYYYMMDD-YYYYMMDD'!"
                return json.dumps({'Error': error_text}), 400, {'ContentType': 'application/json'}
            measure_rows = MeasuresDairyRows.query.filter_by(user_id=g.user.get("User").id, measure_id=measure_id) \
                .filter(MeasuresDairyRows.measure_datetime >= date_from,
                        MeasuresDairyRows.measure_datetime < date_to).order_by(MeasuresDairyRows.measure_datetime.desc()).all()
        else:
            measure_rows = MeasuresDairyRows.query.filter_by(user_id=g.user.get("User").id, measure_id=measure_id).order_by(MeasuresDairyRows.measure_datetime.desc()).all()
        measures_list = list()
        for row in measure_rows:
            measures_list.append({"ID": row.id, "MeasureName": row.measure_name.measure_name,
                                  "MeasureDateTime": row.measure_datetime, "Value": row.value})
        return_dict.update({"Data": measures_list})
        return jsonify(return_dict)
    elif request.method == "POST":  # Добавляем новую запись
        measure_id = request.json.get('MeasureID')
        if Measures.query.filter_by(id=measure_id).first() is None:
            error_text = "Measure type with specified id is not found!"
            return_dict.update({"Data": None, "ErrorCode": 61, "ErrorText": error_text})
            return json.dumps(return_dict), 400, {'ContentType': 'application/json'}
        measure_datetime = request.json.get('MeasureDateTime')
        datetime_format = '%Y%m%d%H%M'
        try:
            measure_datetime = datetime.datetime.strptime(measure_datetime, datetime_format)
        except ValueError:
            error_text = "Unexpected datetime format! Expected 'YYYYMMDDHHMM'!"
            return_dict.update({"Data": None, "ErrorCode": 62, "ErrorText": error_text})
            return json.dumps(return_dict), 400, {'ContentType': 'application/json'}
        value = request.json.get('Value')
        try:
            float(value)
        except ValueError:
            error_text = "Value must be int or float number!"
            return_dict.update({"Data": None, "ErrorCode": 63, "ErrorText": error_text})
            return json.dumps(return_dict), 400, {'ContentType': 'application/json'}
        user_id = g.user.get("User").id
        measure = MeasuresDairyRows(user_id=user_id, measure_id=measure_id, measure_datetime=measure_datetime,
                                    value=value)
        db.session.add(measure)
        db.session.commit()
        return_dict.update({"Data": None, "ErrorCode": 0, "ErrorText": "Value successfuly added!"})
        return json.dumps(return_dict), 200, {'ContentType': 'application/json'}
    elif request.method == "PATCH":  # Редактируем существующую запись
        edit_record_id = request.json.get('ID')
        search_record = MeasuresDairyRows.query.filter_by(id=edit_record_id).first()
        if search_record is None:
            response_code, error_text = 400, "Record not found!"
            return_dict.update({"Data": None, "ErrorCode": 64, "ErrorText": error_text})
        else:
            if search_record.user.id != g.user.get("User").id:
                error_text = "Record not found!"
                return_dict.update({"Data": None, "ErrorCode": 64, "ErrorText": error_text})
                return json.dumps(return_dict), 400, {'ContentType': 'application/json'}
            else:
                if request.json.get('MeasureID') is not None:
                    measure_id = request.json.get('MeasureID')
                    if Measures.query.filter_by(id=measure_id).first() is None:
                        response_code, error_text = 400, "Measure type with specified id is not found!"
                        return_dict.update({"Data": None, "ErrorCode": 61, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
                    else:
                        search_record.measure_id = measure_id
                if request.json.get('MeasureDateTime') is not None:
                    measure_datetime = request.json.get('MeasureDateTime')
                    datetime_format = '%Y%m%d%H%M'
                    try:
                        measure_datetime = datetime.datetime.strptime(measure_datetime, datetime_format)
                        search_record.measure_datetime = measure_datetime
                    except ValueError:
                        response_code, error_text = 400, "Unexpected datetime format! Expected 'YYYYMMDDHHMM'!"
                        return_dict.update({"Data": None, "ErrorCode": 62, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
                if request.json.get('Value') is not None:
                    value = request.json.get('Value')
                    try:
                        float(value)
                        search_record.value = value
                    except ValueError:
                        response_code, error_text = 400, "Value must be int or float number!"
                        return_dict.update({"Data": None, "ErrorCode": 63, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
            db.session.add(search_record)
            db.session.commit()
            response_code, error_text = 200, "Value successfuly edited!"
            return_dict.update({"Data": None, "ErrorCode": 0, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
    elif request.method == "DELETE":  # Удаляем запись
        edit_record_id = request.json.get('ID')
        search_record = MeasuresDairyRows.query.filter_by(id=edit_record_id).first()
        if search_record is None:
            response_code, error_text = 400, "Record not found!"
            return_dict.update({"Data": None, "ErrorCode": 64, "ErrorText": error_text})
        else:
            if search_record.user.id != g.user.get("User").id:
                response_code, error_text = 400, "Record not found!"
                return_dict.update({"Data": None, "ErrorCode": 64, "ErrorText": error_text})
            else:
                db.session.delete(search_record)
                db.session.commit()
                response_code, error_text = 200, "Value successfuly deleted!"
                return_dict.update({"Data": None, "ErrorCode": 0, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}


@app.route('/api/ProductsDairyRows/', methods=["GET", "POST", "PATCH", "DELETE"])
@auth.login_required
def products_dairy_rows():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    if request.method == "GET":  # Получаем данные
        date_format = '%Y%m%d'
        date_interval = request.args.get('date_interval')
        if date_interval:
            try:
                date_interval = date_interval.split("-")
                date_from = datetime.datetime.strptime(date_interval[0], date_format)
                date_to = datetime.datetime.strptime(date_interval[1], date_format)
            except ValueError:
                response_code, error_code = 400, 62
                error_text = "Unexpected date_interval format! Expected 'YYYYMMDD-YYYYMMDD'!"
                return json.dumps({"Data": None,
                                   'ErrorText': error_text,
                                   "ErrorCode": error_code}), response_code, {'ContentType': 'application/json'}
            product_rows = ProductsDairyRows.query.filter_by(user_id=g.user.get("User").id).\
                filter(MeasuresDairyRows.measure_datetime >= date_from,
                       MeasuresDairyRows.measure_datetime < date_to).\
                order_by(MeasuresDairyRows.measure_datetime.desc()).all()
        else:
            product_rows = MeasuresDairyRows.query.filter_by(user_id=g.user.get("User").id).\
                order_by(MeasuresDairyRows.measure_datetime.desc()).all()
        rows_list = list()
        for row in product_rows:
            rows_list.append({"ID": row.id, "ProductName": row.product.name, "DateTime": row.record_datetime,
                              "ProductWeight": row.product_weight,
                              "Callories": row.product_weight * row.product.callories / 100,
                              "Protein": row.product_weight * row.product.protein / 100,
                              "Fat": row.product_weight * row.product.fat / 100,
                              "Carbohydrate": row.product_weight * row.product.carbohydrate / 100})
        response_code, error_code = 200, 0
        error_text = "Success"
        return_dict.update({"Data": rows_list, "ErrorText": error_text, "ErrorCode": error_code})
        return jsonify(return_dict), response_code, {'ContentType': 'application/json'}
    elif request.method == "POST":  # Добавляем новую запись
        user_id = g.user.get("User").id
        input_datetime = request.json.get('RecordDateTime')
        datetime_format = '%Y%m%d%H%M'
        if input_datetime is not None:
            try:  # Проверяем формат переданного значения
                record_datetime = datetime.datetime.strptime(input_datetime, datetime_format)
            except ValueError:
                response_code, error_code, error_text = 400, 62, "Unexpected datetime format! Expected 'YYYYMMDDHHMM'!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
                return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
        else:  # Если параметр не передан, то устанавливаем текущую дату и время
            record_datetime = datetime.datetime.now()
        product_id = request.json.get('ProductID')
        if Products.query.filter_by(id=product_id).first() is None:
            response_code, error_code, error_text = 400, 65, "Product not found!"
            return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
            return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
        product_weight = request.json.get('ProductWeight')
        if product_weight is not None:
            try:
                product_weight = int(product_weight)
            except ValueError:
                response_code, error_code, error_text = 400, 66, "Unexpected weight format! Expected integer!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
                return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
        else:
            response_code, error_code, error_text = 400, 67, "Product weight not specified!"
            return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
            return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
        products_dairy_row = ProductsDairyRows(user_id=user_id, product_id=product_id, record_datetime=record_datetime,
                                               product_weight=product_weight)
        db.session.add(products_dairy_row)
        db.session.commit()
        response_code, error_code, error_text = 200, 0, "Row successfuly added!"
        return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
    elif request.method == "PATCH":  # Редактируем существующую запись
        edit_record_id = request.json.get('ID')
        search_record = ProductsDairyRows.query.filter_by(id=edit_record_id).first()
        if search_record is None:
            response_code, error_code, error_text = 400, 64, "Record not found!"
            return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
        else:
            if search_record.user.id != g.user.get("User").id:  # Принадлежит ли запись пользователю
                response_code, error_code, error_text = 400, 64, "Record not found!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
                return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
            else:
                if request.json.get('ProductID') is not None:
                    product_id = request.json.get('ProductID')
                    if Products.query.filter_by(id=product_id).first() is None:
                        response_code, error_code, error_text = 400, 65, "Product not found!"
                        return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
                    else:
                        search_record.product_id = product_id
                if request.json.get('DairyRowDateTime') is not None:
                    input_datetime = request.json.get('DairyRowDateTime')
                    datetime_format = '%Y%m%d%H%M'
                    try:
                        dairy_row_datetime = datetime.datetime.strptime(input_datetime, datetime_format)
                        search_record.record_datetime = dairy_row_datetime
                    except ValueError:
                        response_code, error_text = 400, "Unexpected datetime format! Expected 'YYYYMMDDHHMM'!"
                        return_dict.update({"Data": None, "ErrorCode": 62, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
                if request.json.get('ProductWeight') is not None:
                    product_weight = request.json.get('ProductWeight')
                    try:
                        int(product_weight)
                        search_record.product_weight = int(product_weight)
                    except ValueError:
                        response_code, error_text = 400, "Weight must be integer number!"
                        return_dict.update({"Data": None, "ErrorCode": 67, "ErrorText": error_text})
                        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
            db.session.add(search_record)
            db.session.commit()
            response_code, error_text = 200, "Row successfuly edited!"
            return_dict.update({"Data": None, "ErrorCode": 0, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
    elif request.method == "DELETE":  # Удаляем запись
        edit_record_id = request.json.get('ID')
        search_record = ProductsDairyRows.query.filter_by(id=edit_record_id).first()
        if search_record is None:
            response_code, error_code, error_text = 400, 64, "Record not found!"
            return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
        else:
            if search_record.user.id != g.user.get("User").id:
                response_code, error_code, error_text = 400, 64, "Record not found!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
            else:
                db.session.delete(search_record)
                db.session.commit()
                response_code, error_code, error_text = 200, 0, "Value successfuly deleted!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}


@app.route('/api/Recipe/', methods=["GET"])
@auth.login_required
def recipe():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    if request.method == "GET":  # Получаем данные
        try:
            recipe_id = int(request.args.get('id'))
        except (ValueError, TypeError):
            response_code, error_code, error_text = 400, 68, "Не передан ID рецепта или неверный формат!"
            return_dict.update({"Data": None, 'ErrorText': error_text, "ErrorCode": error_code})
            return jsonify(return_dict), response_code, {'ContentType': 'application/json'}
        search_result = Recipes.query.filter(Recipes.user_id == g.user.get("User").id, Recipes.id == recipe_id).first()
        response_code, error_code, error_text = 200, 0, None
        return_dict.update({"Data": search_result.get_recipe(), 'ErrorText': error_text, "ErrorCode": error_code})
        return jsonify(return_dict), response_code, {'ContentType': 'application/json'}


@app.route('/api/SearchRecipes/', methods=["GET"])
@auth.login_required
def search_recipes():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    if request.method == "GET":  # Получаем данные
        search_q = request.args.get('q') if request.args.get('q') else ""
        is_private = False if request.args.get('is_private') == "0" else True
        try:
            requested_page = int(request.args.get('page'))
        except TypeError:
            requested_page = 1
        try:
            elements_per_page = int(request.args.get('per_page'))
        except TypeError:
            elements_per_page = 20
        if is_private:
            search_result = Recipes.query.filter(Recipes.user_id == g.user.get("User").id, Recipes.name.like(f"%{search_q}%")).all()
        else:
            search_result = Recipes.query.filter(Recipes.name.like(f"%{search_q}%")).all()
        total_pages = len(search_result) / elements_per_page if len(search_result) % elements_per_page == 0 \
            else len(search_result) // elements_per_page + 1
        curent_page = requested_page if (len(search_result) / elements_per_page) >= requested_page else total_pages
        return_result = search_result[int((curent_page-1)* elements_per_page): int(curent_page * elements_per_page)] \
            if elements_per_page <= len(search_result) else search_result
        response_code, error_code, error_text = 200, 0, None
        return_dict.update({"Data": [recipe_obj.get_recipe_for_list() for recipe_obj in return_result],
                            'ErrorText': error_text, "ErrorCode": error_code, "CurrentPage": curent_page,
                            "TotalPages": total_pages, "TotalFoundRecipes": len(search_result),
                            "RecipesOnPage": elements_per_page})
        return jsonify(return_dict), response_code, {'ContentType': 'application/json'}


@app.route('/api/UseRecipe/', methods=["POST"])
@auth.login_required
def use_recipe():
    return_dict = {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict()
    if request.method == "POST":  # Добавляем новую запись
        user_id = g.user.get("User").id
        input_datetime = request.json.get('RecordDateTime')
        datetime_format = '%Y%m%d%H%M'
        if input_datetime is not None:
            try:  # Проверяем формат переданного значения
                record_datetime = datetime.datetime.strptime(input_datetime, datetime_format)
            except ValueError:
                response_code, error_code, error_text = 400, 62, "Unexpected datetime format! Expected 'YYYYMMDDHHMM'!"
                return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
                return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}
        else:  # Если параметр не передан, то устанавливаем текущую дату и время
            record_datetime = datetime.datetime.now()
        recipe_id = request.json.get('RecipeID')
        if Recipes.query.filter_by(id=product_id).first() is None:
            response_code, error_code, error_text = 400, 69, "Recipe not found!"
            return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
            return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}


        search_result = Recipes.query.filter_by(id=product_id).first()

        print(search_result)
        #products_dairy_row = ProductsDairyRows(user_id=user_id, product_id=product_id, record_datetime=record_datetime,
        #                                       product_weight=product_weight)
        #db.session.add(products_dairy_row)
        #db.session.commit()
        response_code, error_code, error_text = 200, 0, "Row successfuly added!"
        #return_dict.update({"Data": None, "ErrorCode": error_code, "ErrorText": error_text})
        return json.dumps(return_dict), response_code, {'ContentType': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True)
