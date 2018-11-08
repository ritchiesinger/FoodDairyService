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
``` POST /api/Users/ ```
###### BODY
```
{
  "username": "some_user", 
  "password": "qwerty", 
  "email": "some_mail@mail.ru"
}
```
##### Ответ
```
{
    "username": "some_user"
}
```
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
### SearchRecipes
Метод используется для поиска рецептов
#### Параметры
Название | Тип | Описание
------------ | ------------- | -------------
q | String | Поисковой запрос (подстрока), по которому будет производится поиск. Проверяется вхождение подстроки в название рецепта. Если не указать, то вернутся все доступные рецепты, ограниченные другими параметрами метода
is_private | Integer | Флаг, ограничивающий поиск только по своим рецептам (рецептам, которые были созданы текущим пользователем). Если передан 0, то поиск производится по всем рецептам, в остальнеых случаях - только по своим
page | Integer | Номер страницы (среза) выдачи
per_page | Integer | Кол-во элементов на странице (в ответе метода)

#### Пример
##### Запрос
###### URL
```
GET /api/SearchRecipes/?per_page=3&page=2
```
##### Ответ
```
{
    "CurrentPage": 1,
    "Data": [
        {
            "IsPrivate": true,
            "RecipeDescription": "Вариант завтрака с куриными яйцами и овощами",
            "RecipeID": 1,
            "RecipeName": "Яичница с овощами (Завтрак 1)",
            "RecipeOwner": "ritchie_singer"
        },
        {
            "IsPrivate": true,
            "RecipeDescription": "Вариант завтрака с несладким творогом",
            "RecipeID": 2,
            "RecipeName": "Творог (солёный) с овощами (Завтрак 2)",
            "RecipeOwner": "ritchie_singer"
        },
        {
            "IsPrivate": true,
            "RecipeDescription": "Вариант на обед или ужин. Филе трески запекается или готовится на пару. На гарнир - банка зелёного горошка",
            "RecipeID": 3,
            "RecipeName": "Треска с зелёным горошком",
            "RecipeOwner": "ritchie_singer"
        }
    ],
    "ErrorCode": 0,
    "ErrorText": null,
    "RecipesOnPage": 3,
    "TotalFoundRecipes": 3,
    "TotalPages": 1
}
```



