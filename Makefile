run:
	python impressions/manage.py runserver

mig:
	python impressions/manage.py migrate

mm:
	python impressions/manage.py makemigrations

su:
	python manage.py createsuperuser