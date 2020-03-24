from flask import request, jsonify, g, Blueprint
from . import db
from .models import User, Role, Function
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from itertools import chain

bp = Blueprint('main', __name__)
auth = HTTPBasicAuth()


class BusinessErrors(object):
    NOT_ALLOWED = (40101, "Недостаточно прав для запрашиваемого действия!")
    ROLE_NOT_FOUND = (10101, "Указанная роль не найдена!")
    ROLE_ALREADY_EXIST = (10104, "Роль с таким идентификатором уже существует!")
    FUNCTION_ALREADY_EXIST = (10105, "Ролевая функция с таким идентификатором уже существует!")
    FUNCTION_NOT_FOUND = (10106, "Ролевая функция с таким идентификатором не найдена!")
    USER_ROLE_ALREADY_EXIST = (10102, "Указанная роль уже назначена пользователю!")
    USER_ROLE_NOT_FOUND = (10103, "Указанная роль у пользователя не найдена!")
    USER_NOT_FOUND = (20101, "Пользователь не найден!")
    USER_NOT_AUTHORIZED = (20403, "Пользователь не авторизован!")
    USER_ALREADY_EXIST = (20102, "Пользователь с указанным логином уже существует!")
    REQUIRED_PARAMS_ERROR = (30101, "Не переданы некоторые обязательные поля!")


@auth.verify_password
def verify_password(username_or_auth_token, password_or_refresh_token):
    # Сначала пробуем авторизоваться по токену
    user = User.verify_auth_token(secret_key="dev", auth_token=username_or_auth_token,
                                  refresh_token=password_or_refresh_token)
    if not user:
        # А теперь по обычному - логину и паролю
        user = User.query.filter_by(login=username_or_auth_token).first()
        if not user or not user.verify_password(password_or_refresh_token):
            return False
        user = {"User": user}
    g.user = user
    return True


@auth.error_handler
def unauthorized():
    response = jsonify({"Data": None, "ErrorCode": BusinessErrors.USER_NOT_AUTHORIZED[0],
                        "ErrorText": BusinessErrors.USER_NOT_AUTHORIZED[1]})
    return response, 403


@bp.route('/api/SignUp/', methods=["POST"])
def registration():
    login = request.json.get('login')
    password = request.json.get('password')
    email = request.json.get('email')
    error_text, response_data, response_code, error_code = None, None, 200, 1
    if login in (None, "") or password in (None, ""):
        error_text = "login or password is not specified!"
        error_code = 101
    elif User.query.filter_by(login=login).first() is not None:
        error_code = BusinessErrors.USER_ALREADY_EXIST[0]
        error_text = BusinessErrors.USER_ALREADY_EXIST[1]
    elif User.query.filter_by(email=email).first() is not None:
        error_text = f"'{email}' already exist!"
        error_code = 103
    else:
        user = User(login=login, email=email)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        response_code, error_code = 200, 0
        response_data = {"User": {"Login": login, "Email": email}}
        # TODO Надо чтобы ещё назначалась роль USER
    return_dict = {"Data": response_data, "ErrorCode": error_code, "ErrorText": error_text}
    return jsonify(return_dict), response_code, {'ContentType': 'application/json'}


@bp.route('/api/admin/Users/<username>', methods=["GET"])
@auth.login_required
def user_account(username):
    user = User.query.filter_by(login=username).first()
    return_dict = ({"Data": {
        "User": {
            "Login": user.login,
            "Email": user.email,
            "Roles": [{"RoleId": role.id, "ShortId": role.short_id, "Name": role.name,
                       "Functions": [role_func.id for role_func in role.functions]} for role in user.roles]
        }
    }, "ErrorCode": 0, "ErrorText": None})
    return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict())
    return jsonify(return_dict)


@bp.route('/api/admin/UserRole', methods=["POST", "DELETE"])
@auth.login_required
def user_roles_manage():
    all_funcs = tuple(set(chain(*[role.get("Functions") for role in g.user.get("User").to_dict().get("Roles")])))
    if "canManageRoles" not in all_funcs:  # Проверка правомерности
        return_dict = {"ErrorCode": BusinessErrors.NOT_ALLOWED[0],
                       "ErrorText": BusinessErrors.NOT_ALLOWED[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict), 406
    role_id = request.json.get('roleId')
    login = request.json.get('login')
    user = User.query.filter_by(login=login).first()
    # Нашёлся ли пользователь с переданным логином
    if not user:
        return_dict = {"ErrorCode": BusinessErrors.USER_NOT_FOUND[0], "ErrorText": BusinessErrors.USER_NOT_FOUND[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    role = Role.query.filter_by(id=role_id).first()
    # Нашлась ли роль
    if not role:
        return_dict = {"ErrorCode": BusinessErrors.ROLE_NOT_FOUND[0], "ErrorText": BusinessErrors.ROLE_NOT_FOUND[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    # Если всё огонь - делаем то что надо согласно методу
    if request.method == 'POST':  # Добавление роли пользователю
        if role.id in [user_role.id for user_role in user.roles]:  # Наличие роли у пользователя
            return_dict = {"ErrorCode": BusinessErrors.USER_ROLE_ALREADY_EXIST[0],
                           "ErrorText": BusinessErrors.USER_ROLE_ALREADY_EXIST[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        user.roles.append(role)
    else:  # Удаление роли у пользователя
        if role.id not in [user_role.id for user_role in user.roles]:  # Наличие роли у пользователя
            return_dict = {"ErrorCode": BusinessErrors.USER_ROLE_NOT_FOUND[0],
                           "ErrorText": BusinessErrors.USER_ROLE_NOT_FOUND[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        user.roles.remove(role)
    db.session.add(user)
    db.session.commit()
    return_dict = {"ErrorCode": 0, "ErrorText": None}
    return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
    return jsonify(return_dict)


@bp.route('/api/admin/Role/', defaults={'role_id': None}, methods=["GET", "POST"])
@bp.route('/api/admin/Role/<role_id>', methods=["GET", "PATCH", "DELETE"])
@auth.login_required
def roles_manage(role_id=None):
    all_funcs = tuple(set(chain(*[role.get("Functions") for role in g.user.get("User").to_dict().get("Roles")])))
    if "canManageRoles" not in all_funcs:  # Проверка правомерности
        return_dict = {"ErrorCode": BusinessErrors.NOT_ALLOWED[0],
                       "ErrorText": BusinessErrors.NOT_ALLOWED[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict), 406
    if request.method == 'GET':  # Получение данных по ролям из БД
        if role_id:  # Получение данных по конкретной роли
            role = Role.query.filter_by(id=role_id).first()
            return_dict = ({"Data": {"Role": role.to_dict()}, "ErrorCode": 0, "ErrorText": None})
            return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")}
                                           if g.user.get("NewTokens") else dict())
        else:  # Поиск ролей по фильтру
            request_params = dict((item[0].lower(), item[1].lower()) for item in request.args.items())
            role_id_filter = f"%{request_params.get('id') if request_params.get('id') else ''}%"
            role_name_filter = f"%{request_params.get('name') if request_params.get('name') else ''}%"
            role_short_id_filter = f"%{request_params.get('shortid') if request_params.get('shortid') else ''}%"
            page_filter = int(request_params.get('page')) if request_params.get('page') else 1
            per_page_filter = int(request_params.get('perpage')) if request_params.get('perpage') else 10
            all_roles = Role.query.filter(Role.id.like(role_id_filter)).filter(Role.name.like(role_name_filter))\
                .filter(Role.short_id.like(role_short_id_filter))
            all_roles_count = all_roles.count()
            total_pages = all_roles_count // per_page_filter \
                if all_roles_count % per_page_filter == 0 else all_roles_count // per_page_filter + 1
            request_result = Role.query.filter(Role.id.like(role_id_filter)).filter(Role.name.like(role_name_filter))\
                .filter(Role.short_id.like(role_short_id_filter)).paginate(page_filter, per_page_filter, False).items
            return_dict = ({"Data": {"Roles": [role.to_dict() for role in request_result],
                                     "Page": page_filter, "TotalPages": total_pages},
                            "ErrorCode": 0, "ErrorText": None})
            return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")}
                                           if g.user.get("NewTokens") else dict())
        return jsonify(return_dict)
    elif request.method == 'POST':  # Создание новой роли
        role_id = request.json.get('id')
        role_name = request.json.get('name')
        role_description = request.json.get('description')
        role_short_id = request.json.get('shortId')
        if not (role_id and role_name and role_short_id):
            return_dict = {"ErrorCode": BusinessErrors.REQUIRED_PARAMS_ERROR[0],
                           "ErrorText": BusinessErrors.REQUIRED_PARAMS_ERROR[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        role = Role(id=role_id, name=role_name, description=role_description, short_id=role_short_id)
        try:
            db.session.add(role)
            db.session.commit()
            return_dict = {"ErrorCode": 0, "ErrorText": None}
        except IntegrityError:
            return_dict = {"ErrorCode": BusinessErrors.ROLE_ALREADY_EXIST[0],
                           "ErrorText": BusinessErrors.ROLE_ALREADY_EXIST[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    elif request.method == 'PATCH':  # Редактирование существующей роли
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return_dict = {"ErrorCode": BusinessErrors.ROLE_NOT_FOUND[0], "ErrorText": BusinessErrors.ROLE_NOT_FOUND[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        # Для редактирования роли нужен хотя бы один новый параметр
        if not (request.json.get('name') or request.json.get('description') or request.json.get('shortId')):
            return_dict = {"ErrorCode": BusinessErrors.REQUIRED_PARAMS_ERROR[0],
                           "ErrorText": BusinessErrors.REQUIRED_PARAMS_ERROR[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        role.name = request.json.get('name') if request.json.get('name') else role.name
        role.description = request.json.get('description') if request.json.get('description') else role.description
        role.short_id = request.json.get('shortId') if request.json.get('shortId') else role.short_id
        db.session.commit()
        return_dict = {"ErrorCode": 0, "ErrorText": None}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    else:  # Удаление роли
        role = Role.query.filter_by(id=role_id).first()
        try:
            db.session.delete(role)
            db.session.commit()
            return_dict = {"ErrorCode": 0, "ErrorText": None}
        except UnmappedInstanceError:
            return_dict = {"ErrorCode": BusinessErrors.ROLE_NOT_FOUND[0], "ErrorText": BusinessErrors.ROLE_NOT_FOUND[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)


@bp.route('/api/admin/Function/', defaults={'func_id': None}, methods=["GET", "POST"])
@bp.route('/api/admin/Function/<func_id>', methods=["GET", "PATCH", "DELETE"])
@auth.login_required
def functions_manage(func_id=None):
    all_funcs = tuple(set(chain(*[role.get("Functions") for role in g.user.get("User").to_dict().get("Roles")])))
    if "canManageFunctions" not in all_funcs:  # Проверка правомерности
        return_dict = {"ErrorCode": BusinessErrors.NOT_ALLOWED[0],
                       "ErrorText": BusinessErrors.NOT_ALLOWED[1]}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict), 406
    if request.method == 'GET':  # Получение данных по ролевым функциям из БД
        if func_id:  # Получение данных по конкретной функции
            role_func = Function.query.filter_by(id=func_id).first()
            return_dict = ({"Data": {"Function": role_func.to_dict()}, "ErrorCode": 0, "ErrorText": None})
            return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")}
                                           if g.user.get("NewTokens") else dict())
        else:  # Поиск функций по фильтру
            request_params = dict((item[0].lower(), item[1].lower()) for item in request.args.items())
            function_id_filter = f"%{request_params.get('id') if request_params.get('id') else ''}%"
            page_filter = int(request_params.get('page')) if request_params.get('page') else 1
            per_page_filter = int(request_params.get('perpage')) if request_params.get('perpage') else 10
            all_functions = Function.query.filter(Function.id.like(function_id_filter))
            all_functions_count = all_functions.count()
            total_pages = all_functions_count // per_page_filter \
                if all_functions_count % per_page_filter == 0 else all_functions_count // per_page_filter + 1
            request_result = Function.query.filter(Function.id.like(function_id_filter))\
                .paginate(page_filter, per_page_filter, False).items
            return_dict = ({"Data": {"Functions": [function.to_dict() for function in request_result],
                                     "Page": page_filter, "TotalPages": total_pages},
                            "ErrorCode": 0, "ErrorText": None})
            return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")}
                                           if g.user.get("NewTokens") else dict())
        return jsonify(return_dict)
    elif request.method == 'POST':  # Создание новой функции
        function_id = request.json.get('id')
        function_description = request.json.get('description')
        if not function_id:
            return_dict = {"ErrorCode": BusinessErrors.REQUIRED_PARAMS_ERROR[0],
                           "ErrorText": BusinessErrors.REQUIRED_PARAMS_ERROR[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        function = Function(id=function_id, description=function_description)
        try:
            db.session.add(function)
            db.session.commit()
            return_dict = {"ErrorCode": 0, "ErrorText": None}
        except IntegrityError:
            error_code, error_text = BusinessErrors.FUNCTION_ALREADY_EXIST[0], BusinessErrors.FUNCTION_ALREADY_EXIST[1]
            return_dict = {"ErrorCode": error_code, "ErrorText": error_text}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    elif request.method == 'PATCH':  # Редактирование существующей роли
        function = Function.query.filter_by(id=func_id).first()
        if not function:
            error_code, error_text = BusinessErrors.FUNCTION_NOT_FOUND[0], BusinessErrors.FUNCTION_NOT_FOUND[1]
            return_dict = {"ErrorCode": error_code, "ErrorText": error_text}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        # Для редактирования роли нужен хотя бы один новый параметр
        function_description = request.json.get('description')
        if not function_description:
            return_dict = {"ErrorCode": BusinessErrors.REQUIRED_PARAMS_ERROR[0],
                           "ErrorText": BusinessErrors.REQUIRED_PARAMS_ERROR[1]}
            return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
            return jsonify(return_dict)
        function.description = function_description if function_description else function.description
        db.session.commit()
        return_dict = {"ErrorCode": 0, "ErrorText": None}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)
    else:  # Удаление функции
        function = Function.query.filter_by(id=func_id).first()
        try:
            db.session.delete(function)
            db.session.commit()
            return_dict = {"ErrorCode": 0, "ErrorText": None}
        except UnmappedInstanceError:
            error_code, error_text = BusinessErrors.FUNCTION_NOT_FOUND[0], BusinessErrors.FUNCTION_NOT_FOUND[1]
            return_dict = {"ErrorCode": error_code, "ErrorText": error_text}
        return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else None})
        return jsonify(return_dict)


@bp.route('/api/admin/Users/', methods=["GET"])
@auth.login_required
def users():
    request_params = dict((item[0].lower(), item[1].lower()) for item in request.args.items())
    login_filter = f"%{request_params.get('login') if request_params.get('login') else ''}%"
    email_filter = f"%{request_params.get('email') if request_params.get('email') else ''}%"
    page_filter = int(request_params.get('page')) if request_params.get('page') else 1
    per_page_filter = int(request_params.get('perpage')) if request_params.get('perpage') else 10
    request_result = User.query.filter(User.login.like(login_filter)).filter(User.email.like(email_filter)).all()
    total_pages = len(request_result) // per_page_filter + (1 if len(request_result) % per_page_filter != 0 else 0)
    if len(request_result) <= per_page_filter:
        current_page = 1
        return_result = request_result
    else:
        pages_list = list()
        page_list = list()
        for user in request_result:
            page_list.append(user)
            if len(page_list) == per_page_filter:
                pages_list.append(page_list)
                page_list = []
        else:
            pages_list.append(page_list)
            current_page = page_filter if len(pages_list) >= page_filter else total_pages
        return_result = pages_list[current_page - 1]
    users_list = [{"Login": user.login,
                   "Email": user.email,
                   "Roles": [{"RoleId": role.id, "ShortId": role.short_id, "Name": role.name,
                              "Functions": [role_func.id for role_func in role.functions]}
                             for role in user.roles]} for user in return_result]
    return_dict = ({"Data": {"UsersList": users_list, "TotalPages": total_pages, "Page": current_page},
                    "ErrorCode": 0, "ErrorText": None})
    return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")} if g.user.get("NewTokens") else dict())
    return jsonify(return_dict)


@bp.route('/api/GetToken/', methods=['GET'])
@auth.login_required
def get_tokens():
    tokens = g.user.get("User").generate_tokens(secret_key="dev", is_refresh="All")
    return_dict = {"Data": {"AuthToken": tokens.get("AuthToken"),
                            "RefreshToken": tokens.get("RefreshToken"),
                            "User": {"Login": g.user.get("User").login, "Email": g.user.get("User").email},
                            "Roles": [{"RoleId": role.id, "ShortId": role.short_id,
                                       "Functions": [role_func.id for role_func in role.functions]}
                                      for role in g.user.get("User").roles]},
                   "ErrorCode": 0, "ErrorText": None}
    return jsonify(return_dict)


@bp.route('/api/SetNewPassword/', methods=["POST"])
@auth.login_required
def set_new_password():
    """ Метод установки нового пароля. Требуется авторизация. На вход ожидает JSON вида: {"password": "somepassword"}
    :return: Стандартный контракт вида:  {"data": None, "ErrorCode": 0, "ErrorText": "New password is set!"} """
    new_password = request.json.get('password')
    user = User.query.filter_by(login=g.user.get("User").login).first()
    user.hash_password(new_password)
    db.session.commit()
    return_dict = ({"Data": None, "ErrorCode": 0, "ErrorText": None})
    return_dict.update({"Data": {"NewTokens": g.user.get("NewTokens")}} if g.user.get("NewTokens") else dict())
    return jsonify(return_dict)


@bp.route("/api/GetMyProfile/")
@auth.login_required
def get_my_profile():
    return_dict = {"Data": {
        "Login": g.user.get("User").login,
        "Email": g.user.get("User").email,
        "Roles": [{"RoleId": role.id, "Functions": [role_func.id for role_func in role.functions]}
                  for role in g.user.get("User").roles]}}
    return_dict.update({"ErrorCode": 0, "ErrorText": None})
    if g.user.get("NewTokens"):
        return_dict.get("Data").update({"NewTokens": g.user.get("NewTokens")})
    return jsonify(return_dict)


'''
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
       #send_mail(recipients=["ritchie_singer@mail.ru"], subject="Восстановление пароля к сервису FoodDairy", html=html)
        return jsonify({"data": f"New password '{new_password}' send to {email}!"})
'''
