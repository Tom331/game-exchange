<<<<<<< HEAD
release: python3 manage.py migrate
web: daphne django_project.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python3 manage.py runworker channels --settings=django_project.settings -v2
=======
release: python manage.py migrate
web: daphne core.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels --settings=core.settings -v2
>>>>>>> f63def76365a5dbaf714975304c677ace7b3d167
