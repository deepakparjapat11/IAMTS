# Configuration IAMTS Backend and Frontend:

# IAMTS supports django 3.1.4, python 3.6.10 and my sql.

    IAMTS Config steps
    Step 1: Take pull 
    Step 2: create virtual environment ( virtualenv -p python3.6 env ) 
    Step 3: Activate virtual environment(source env/bin/activate)
    Step 4: install requirements(pip install -r requirements.txt)
    Step 5: Make migrations(1. python manage.py makemigrations 2. python manage.py migrate)
    step 6: run server (python manage.py runserver 0:port no)

# Rename example.env to .env Configure .evn file Run

OR

# Configuration Env file

    SECRET_KEY = ’your secret key for encryption’
    Database configuration
    DB_USER = ‘User name’
    DB_PWD = ‘password’
    DB_NAME = ‘database name’
    DB_HOST = ‘host name’
    DB_PORT = ‘port number of db’
    
    Email configurations 
    EMAIL_HOST = ’smtp.example.com’
    EMAIL_HOST_USER = ‘username(example@example.com'
    EMAIL_HOST_PASSWORD = 'your password'
    EMAIL_FROM = EMAIL_HOST_USER
    ALLOWED_HOSTS = ‘your hosts’



# List of Services under IAMTS:
    BACKEND AND FRONTEND
    MYSQL


BACKEND AND FRONTEND

# working
    IAMTS is a service which manages User Auth, User Profile, Bus Records, Work order, Roster management, services, backend api etc.

    Configuration:
	    Language: Python 3.6.10
	    Framework: Django 3.1.4

    MYSQL
    Working:
	    MYSQL is used as a primary database.

    Configuration:
        Engine: MYSQL
        version : mysqlclient 2.0.2
