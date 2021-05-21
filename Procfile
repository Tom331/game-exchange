release: python3 manage.py migrate
web: daphne django_project.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python3 manage.py runworker channels --settings=django_project.settings -v2
