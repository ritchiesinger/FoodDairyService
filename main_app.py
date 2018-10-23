from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import json
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fooddairydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "Very Secret Key"
db = SQLAlchemy(app)


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

    def generate_auth_token(self, expiration=600):  # 600 секунд на пртухание
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # Токен протух
        except BadSignature:
            return None  # Неверный токен
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return f"<User {self.username}>"


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
def get_token():
    token = g.user.generate_auth_token()
    return jsonify({"data": {'AuthToken': token.decode('ascii')}})


@auth.verify_password
def verify_password(username_or_token, password):
    # Сначала пробуем авторизоваться по токену
    user = User.verify_auth_token(username_or_token)
    if not user:
        # А теперь по обычному - логину и паролю
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route("/api/GetMyProfile/")
@auth.login_required
def get_my_profile():
    return jsonify({"data": {"UserName": g.user.username, "Email": g.user.email}})


@app.route("/api/GetMeasureValues/", methods=['GET'])
@auth.login_required
def get_measure_values():
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
        measure_rows = MeasuresDairyRows.query.filter_by(user_id=g.user.id, measure_id=measure_id) \
            .filter(MeasuresDairyRows.measure_datetime >= date_from, MeasuresDairyRows.measure_datetime < date_to).all()
    else:
        measure_rows = MeasuresDairyRows.query.filter_by(user_id=g.user.id, measure_id=measure_id).all()
    measures_list = list()
    for row in measure_rows:
        measures_list.append({"MeasureName": row.measure_name.measure_name, "MeasureDateTime": row.measure_datetime,
                              "Value": row.value})
    return jsonify({"data": measures_list})


@app.route('/api/AddMeasureValue/', methods=['POST'])
@auth.login_required
def add_measure_value():
    measure_id = request.json.get('measure_id')
    measure_datetime = request.json.get('measure_datetime')
    value = request.json.get('value')
    user_id = g.user.id
    measure = MeasuresDairyRows(user_id=user_id, measure_id=measure_id, measure_datetime=measure_datetime, value=value)
    db.session.add(measure)
    db.session.commit()
    return jsonify({'username': user.username}), 201


if __name__ == "__main__":
    app.run(debug=True)
