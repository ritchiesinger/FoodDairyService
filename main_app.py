from flask import Flask, request, jsonify, g
import json
import datetime
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail, Message
import random
from config import Config
from models import db, User, Measures, MeasuresDairyRows, Products, ProductsDairyRows, Recipes


def create_app(app_config, app_db):
    return_app = Flask(__name__)
    return_app.config.from_object(app_config)
    app_db.init_app(return_app)
    return {"app": return_app, "db": app_db}


auth = HTTPBasicAuth()
create_result = create_app(Config(), db)
app = create_result.get("app")
mail = Mail(app)


def password_generator():
    avaliable_symbols = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    password_lenght = 8
    generated_password = "".join(random.sample(avaliable_symbols, password_lenght))
    return generated_password


def send_mail(recipients, subject, html):
    msg = Message(subject=subject, recipients=recipients, html=html)
    with app.app_context():
        mail.send(msg)


@auth.verify_password
def verify_password(username_or_auth_token, password_or_refresh_token):
    # Сначала пробуем авторизоваться по токену
    user = User.verify_auth_token(secret_key=app.config["SECRET_KEY"], auth_token=username_or_auth_token,
                                  refresh_token=password_or_refresh_token)
    if not user:
        # А теперь по обычному - логину и паролю
        user = User.query.filter_by(username=username_or_auth_token).first()
        if not user or not user.verify_password(password_or_refresh_token):
            return False
        user = {"User": user}
    g.user = user
    return True


@app.route('/', methods=['GET'])
def app_test():
    return jsonify({"Data": "Hello FoodDairyService!"}), 200


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
    tokens = g.user.get("User").generate_tokens(secret_key=app.config["SECRET_KEY"], is_refresh="All")
    return jsonify({"data": {"AuthToken": tokens.get("AuthToken"), "RefreshToken": tokens.get("RefreshToken")}})


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
    return_dict.update({"data": {"UserName": g.user.get("User").username, "Email": g.user.get("User").email}})
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
                .filter(
                    MeasuresDairyRows.measure_datetime >= date_from,
                    MeasuresDairyRows.measure_datetime < date_to
                ).order_by(MeasuresDairyRows.measure_datetime.desc()).all()
        else:
            measure_rows = MeasuresDairyRows.query.filter_by(
                user_id=g.user.get("User").id,
                measure_id=measure_id
            ).order_by(
                MeasuresDairyRows.measure_datetime.desc()
            ).all()
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
            search_result = Recipes.query.filter(Recipes.user_id == g.user.get("User").id,
                                                 Recipes.name.like(f"%{search_q}%")).all()
        else:
            search_result = Recipes.query.filter(Recipes.name.like(f"%{search_q}%")).all()
        total_pages = len(search_result) / elements_per_page if len(search_result) % elements_per_page == 0 \
            else len(search_result) // elements_per_page + 1
        curent_page = requested_page if (len(search_result) / elements_per_page) >= requested_page else total_pages
        return_result = search_result[int((curent_page-1)*elements_per_page): int(curent_page * elements_per_page)] \
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
