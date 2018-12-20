from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

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
            result = {"AuthToken": auth_token.dumps({'id': self.id}).decode('ascii')}
        elif is_refresh is True:
            refresh_token = Serializer(secret_key + "refresh", expires_in=expiration * 3)
            result = {"RefreshToken": refresh_token.dumps({'id': self.id}).decode('ascii')}
        else:
            auth_token = Serializer(secret_key, expires_in=expiration)
            refresh_token = Serializer(secret_key + "refresh", expires_in=expiration * 3)
            result = {"AuthToken": auth_token.dumps({'id': self.id}).decode('ascii'),
                      "RefreshToken": refresh_token.dumps({'id': self.id}).decode('ascii')}
        return result

    @staticmethod
    def verify_auth_token(auth_token, refresh_token, secret_key):
        auth_token_check = Serializer(secret_key)
        return_dict = dict()
        try:
            data = auth_token_check.loads(auth_token)
            user = User.query.get(data['id'])
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
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return f"<User {self.username}>"


class Measures(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    measure_name = db.Column(db.String(128), unique=True, nullable=False)
    measure_dimension = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Measures: {self.measure_name}>"


class MeasuresDairyRows(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    measure_datetime = db.Column(db.DateTime, nullable=False)
    measure_id = db.Column(db.Integer, db.ForeignKey('measures.id'), nullable=False)
    value = db.Column(db.REAL, nullable=False)
    user = db.relationship("User", foreign_keys=user_id)
    measure_name = db.relationship("Measures", foreign_keys=measure_id)

    def __repr__(self):
        return f"<MeasuresDairyRows {self.user.username}: {self.id} ({self.measure_datetime})>"


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = db.Column(db.String(128), unique=True, nullable=False)
    callories = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.REAL, nullable=False)
    protein = db.Column(db.REAL, nullable=False)
    carbohydrate = db.Column(db.REAL, nullable=False)
    description = db.Column(db.Text)
    image_link = db.Column(db.Text)
    disabled = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Products {self.id} ({self.name})>"


class ProductsDairyRows(db.Model):
    __tablename__ = "products_dairy_rows"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    record_datetime = db.Column(db.DateTime, nullable=False)
    product_weight = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", foreign_keys=user_id)
    product = db.relationship("Products", foreign_keys=product_id)

    def __repr__(self):
        return f"<ProductDairyRows {self.user.username} ({self.id}): {self.record_datetime} >"


class Recipes(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_private = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.Text)
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_weight = db.Column(db.Integer, nullable=False)
    product = db.relationship("Products", foreign_keys=product_id)
    recipe = db.relationship("Recipes", foreign_keys=recipe_id)

    def __repr__(self):
        return f"<RecipesProducts {self.recipe_id}: {self.product_id}>"
