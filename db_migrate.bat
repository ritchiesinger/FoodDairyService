CALL venv/scripts/activate.bat
SET FLASK_APP=service
SET FLASK_ENV=development
flask db migrate
flask db upgrade