from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

db = SQLAlchemy()

users_roles = db.Table('users_roles',
                       db.Column('login', db.String(32), db.ForeignKey('user.login'), primary_key=True),
                       db.Column('role_id', db.String(32), db.ForeignKey('roles.id'), primary_key=True))

roles_functions = db.Table('roles_functions',
                           db.Column('role_id', db.String(32), db.ForeignKey('roles.id'), primary_key=True),
                           db.Column('function_id', db.String(64), db.ForeignKey('functions.id'), primary_key=True))


class User(db.Model):
    __tablename__ = "user"
    login = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    roles = db.relationship('Role', secondary=users_roles, lazy='subquery', backref=db.backref('user', lazy=True))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_tokens(self, secret_key, is_refresh=False, expiration=60):  # 60 секунд на пртухание
        """ Генерация токенов
        :param secret_key: секретная строка (обычно из конфига берётся)
        :param is_refresh: параметр, определяющий какой токен надо сгенерировать. True - будет сгенерирован
        refresh-токен, False - будет сгенерирован auth-токен. Любое другое значение - будут сгенерированы оба токена.
        :param expiration: время протухания auth токена в секундах. Время протухания refresh токена принимается в 3
        раза больше.
        :return: в зависимости от входящих параметров вернётся либо какой-то один из токенов, либо оба. """
        if is_refresh is False:
            auth_token = Serializer(secret_key, expires_in=expiration)
            result = {"AuthToken": auth_token.dumps({'login': self.login}).decode('ascii')}
        elif is_refresh is True:
            refresh_token = Serializer(secret_key + "refresh", expires_in=expiration * 3)
            result = {"RefreshToken": refresh_token.dumps({'login': self.login}).decode('ascii')}
        else:
            auth_token = Serializer(secret_key, expires_in=expiration)
            refresh_token = Serializer(secret_key + "refresh", expires_in=expiration * 3)
            result = {"AuthToken": auth_token.dumps({'login': self.login}).decode('ascii'),
                      "RefreshToken": refresh_token.dumps({'login': self.login}).decode('ascii')}
        return result

    @staticmethod
    def verify_auth_token(auth_token, refresh_token, secret_key):
        auth_token_check = Serializer(secret_key)
        return_dict = dict()
        try:
            data = auth_token_check.loads(auth_token)
            user = User.query.get(data['login'])
            return_dict.update({"User": user})
            try_refresh_token = user.verify_refresh_token(refresh_token, secret_key)
            if try_refresh_token is None:
                new_tokens = user.generate_tokens(secret_key=secret_key, is_refresh=True)
                return_dict.update({"NewTokens": new_tokens})
            return return_dict
        except (SignatureExpired, BadSignature):
            try_refresh_token = User.verify_refresh_token(refresh_token, secret_key)
            if try_refresh_token is not None:
                new_tokens = try_refresh_token.generate_tokens(secret_key=secret_key)
                return {"User": try_refresh_token, "NewTokens": new_tokens}
            else:
                return None

    @staticmethod
    def verify_refresh_token(refresh_token, secret_key):
        refresh_token_check = Serializer(secret_key + "refresh")
        try:
            data = refresh_token_check.loads(refresh_token)
        except SignatureExpired:
            return None  # Токен протух
        except BadSignature:
            return None  # Неверный токен
        user = User.query.get(data['login'])
        return user

    def __repr__(self):
        return f"<User {self.login}>"

    def to_dict(self):
        return {"Login": self.login, "Email": self.email, "Roles": [role.to_dict() for role in self.roles]}


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
    short_id = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    functions = db.relationship('Function', secondary=roles_functions, lazy='dynamic',
                                backref=db.backref('roles', lazy='dynamic'))

    def __repr__(self):
        return f"<Role {self.id} ({self.name})>"

    def to_dict(self):
        return {"Id": self.id, "Name": self.name, "Description": self.description, "ShortId": self.short_id,
                "Functions": [role_func.id for role_func in self.functions]}


class Function(db.Model):
    __tablename__ = "functions"
    id = db.Column(db.String(64), primary_key=True, unique=True, nullable=False)
    description = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f"Ролевая функция:\nid='{self.id}'\ndescription='{self.description}'"

    def to_dict(self):
        return {"Id": self.id, "Description": self.description}
