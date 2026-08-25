run:
	cd impressions && python manage.py runserver

mig:
	cd impressions && python manage.py migrate

mm:
	cd impressions && python manage.py makemigrations

su:
	cd impressions && python manage.py createsuperuser

test:
	cd impressions && python manage.py test
	black .