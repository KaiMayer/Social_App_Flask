Quick guide on gow to run:

1. create venv
2. pip install -r requirements.txt
3. export FLASK_APP=social_app.py
4. flask db init
5. flask db migrate
6. flask upgrade
7. flask shell <br>
... `Role.insert_roles()`<br>
... `exit()`
8. flask run