# Interview Assignment - Tester Matching
A REST API developed using the Django framework as a take home assigment for a job interview back in 2019.
## Assumptions
- Times in `testers.csv` file are in UTC timezone.
- Testers could report a bug on a device that they no longer own
- If a tester doesn't own a device anymore the bugs related to this device don't count towards experience
## Technologies used

### REST API:
- Python 3
- Django 
- Django REST framework
- drf-yasg - Yet another Swagger generator
### Database:
- PostgreSQL
### Other tools:
- Docker
- Docker Compose
- Nginx
- Gunicorn
## API schema
### [GET] <ip/domain>/match-testers/
Returns list of testers ordered by experience. It can take two query parameters:

#### Query parameters:
- devices `(array[integer])` - devices for which experience should be calculated, empty means all devices
- countries `(array[string]` - countries from which testers should be included, empty means any country

Example query: `<ip/domain>/match-testers?devices=3&devices=2&countries=GB&countries=JP`

### [GET] <ip/domain>/devices/
Returns list of all available devices

## Data model
I've defined 3 simple database models:
- Tester
- Device
- Bug

Many to many relation between Testers and Devices is defined using Django's manytomany field which internally creates a database table. Countries are defined as a simple tuple inside the code. 
## Using the API
The easiest way to test and explore the API is to use swagger: `<ip/domain>/swagger/`.

Browsing the API:
![alt text](DocumentationImages/swagger1.PNG?raw=true "Swagger - Browsing the API")

Making a request:
![alt text](DocumentationImages/swagger2.PNG?raw=true "Swagger - Making a request")
## Importing the data
Data can be imported using custom django-admin command called `populate_db`. 

You can run it the same way you would run any other django-admin command.
```shell
python manage.py populate_db
```
Script requires the database tables to be empty to avoid collisions and to avoid populating database twice by mistake.  If tables are not empty script throws an error.
## Running the app
App requires PostgreSQL database. Because of that the easiest way to run it locally is to use Docker Compose. 

First, open terminal in the TeststerMatch directory. 

To start the app in a development mode run this commands:
```shell
cp db.env.template db.env
cp dev.env.template dev.env
docker-compose up
```
After docker containers are up, you need to run these two commands in another terminal to setup the database.
```shell
docker-compose exec web python manage.py migrate
```
```shell
docker-compose exec web python manage.py populate_db
```

API url: http://127.0.0.1:8000/swagger/
## Running tests
After starting Docker Compose and running migration command, you can run tests inside Docker using command bellow.
```shell
docker-compose exec web python manage.py test
```
## Running the app in a production-like setup
I think it's a good idea to show something more than just a working Django development server. I've created a second docker-compose file which is much closer to an actually deployed app.

It uses Gunicorn to serve the application and Nginx as web server.

To start app in a production mode run this commands:
```shell
cp db.env.template db.env
cp prod.env.template prod.env
docker-compose -f docker-compose-prod.yml up
```
Next two steps are pretty much the same as for the development mode.
```shell
docker-compose -f docker-compose-prod.yml exec web python manage.py migrate
```
```shell
docker-compose -f docker-compose-prod.yml exec web python manage.py populate_db
```
Production mode requires one additional step which setups static files
```shell
docker-compose -f docker-compose-prod.yml exec web python manage.py collectstatic
```
You will need to enter `yes` to confirm this command.

API url: http://127.0.0.1:1337/swagger/
