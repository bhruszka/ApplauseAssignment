# Applause Assignment - Tester Matching
A REST API developed using Django framework.
## Assumptions
- Times in `testers.csv` file are in UTC timezone.
- Testers could reported a bug on a divice that they no longer own
- If tester doesn't own a device anymore bugs related to this device don't count towards expirience
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
Returns list of testers ordered by experience. It can take two query parameters: countries and

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

Many to many relation between Testers and Devices is defined using Django's manytomany field which internally creates a database table. Countries are defined as simple tuple inside the code. 
## Using the API
The easiest way to test and explore the API is to use the swagger endpoint: `<ip/domain>/swagger/`.

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
Script requires the database tables to be empty to avoid collisions and to avoid populating database twice by mistake.  If tables are not empty script throughs an error.
## Running the app
App requires PostgreSQL database. Because of that the easiest way to run it locally is to use Docker Compose. 

First open terminal in the TeststerMatch directory. 

To start the app in a development mode run this command:
```shell
docker-compose up
```
After docker containers are up. You need to run this two commands in other terminal in the same directory to setup the database.
```shell
docker-compose exec web python manage.py migrate
```
```shell
docker-compose exec web python manage.py populate_db
```
## Running tests
After starting Docker Compose and running migration command. You can run tests inside Docker using command bellow.
```shell
docker-compose exec web python manage.py test
```
## Running the app in production-like setup
I think it's a good idea to show something more than just working Django development server. So I've created 2nd docker-compose file which is much closer to an actually deployed app.

It uses Gunicorn to server the application and Nginx as web server.

To start app in a production mode run this command:
```shell
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
