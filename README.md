# Step 1: install a virtual environment then activate it

# Step 2: besides python and django, install rest_framework, corsheaders (for server security), knox (for authentication), dotenv (for creating environment variables), and simple email confirmation.

Run: `pip install djangorestframework django-cors-headers django-rest-knox python-dotenv django-simple-email-confirmation`

# Step 3: create a a file called ".env" in /pinkwaves

Then, inside of ".env", put these 2 lines:

```
export EMAIL_HOST_PASSWORD = password for host email in string quotes
export EMAIL_HOST_USER = host email in string quotes
```

If your gmail host isn't working, go to this link to allow Python sending emails from your gmail: https://www.google.com/settings/security/lesssecureapps

# Step 4: **DO THIS BEFORE RUNNING ANY COMMANDS FROM python manage.py**

Run: `python manage.py makemigrations accounts relationships userMessages`

# Step 5: run python manage.py migrate

# Step 6: run python manage.py createsuperuser and then input your personal development login credentials

To run backend: `python manage.py runserver.`