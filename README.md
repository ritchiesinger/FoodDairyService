# FoodDairyService

FoodDairyService является учебным проектом для освоения фреймворка Flask. MVP проекта - сервис и REST API к нему, который будет иметь методы для аутентификации пользователей, а таккже методы которые позволят вести дневники веса и произвольных измерений тела - получение данных и внесение данных.
## Методы

На текущий момент реализованы следующие методы:
* Users
* GetToken
* GetMyProfile
* GetMeasureValues

### Users

Метод используется для регистрации нового пользователя в системе

#### Параметры

Название | Описание
------------ | -------------
username | Логин пользователя. будет в дальнейшем использоваться для авторизации
password | Пароль
email | Адрес электронной почты

#### Пример

##### Запрос

###### URL

 POST /api/Users/ 

###### BODY


{
  "username": "some_user", 
  "password": "qwerty", 
  "email": "some_mail@mail.ru"
}


##### Ответ


{
    "username": "some_user"
}


### GetToken

Метод используется для получения пары временных токенов (AuthToken и RefreshToken) для использования их как реквизитов авторизованных запросов вместо логина и пароля.

#### Параметры
Кроме реквизитов доступа никаких параметров не передаётся

#### Пример

##### Запрос

###### URL

```
GET /api/GetToken/
```

##### Ответ

```
{
    "data": {
        "AuthToken": "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0MTYwMjY0MCwiZXhwIjoxNTQxNjAyNzAwfQ.eyJpZCI6Mn0.3ikJgidocnslA5ztr",
        "RefreshToken": "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0MTYwMjY0MCwiZXhwIjoxNTQxNjAyODIwfQ.eyJpZCI6Mn0.rF_KEvHaNRE5Gf"
    }
}
```
