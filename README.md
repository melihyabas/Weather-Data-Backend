# Weather Data Backend


This back-end project is a design of REST API endpoints that handle Authentication and CRUD operations for generated
time series weather data.

### End Points
* User credential (username and password) submission endpoint that is exposed at /login (POST).
* User create endpoint is exposed at /user (POST).
* User information endpoint is exposed at /user/{user_id} (GET).
* Updating user information endpoint is exposed at /user/{user_id} (PUT/POST).
* Deleting the user endpoint is exposed at /user/{user_id} (DELETE).
* Weather information endpoint is exposed at /weather (GET) and can be filtered by given
parameters (condition, time range, location, average etc.).


## How to Run This Project?

Clone and open up this repository into your local machine.

Install requirements using terminal
```
 pip install -r requirements.txt

```

Open a database manager like PgAdmin4

Create a database using credentials in app.py.

![ss1](https://github.com/melihyabas/Weather-Data-Backend/blob/main/databasecreation/credent.PNG?raw=true)

![ss1](https://github.com/melihyabas/Weather-Data-Backend/blob/main/databasecreation/ss1.PNG?raw=true)
Right click on db and select restore.
![ss1](https://github.com/melihyabas/Weather-Data-Backend/blob/main/databasecreation/ss2.PNG?raw=true)
Select database.sql and save it.
![ss1](https://github.com/melihyabas/Weather-Data-Backend/blob/main/databasecreation/ss3.PNG?raw=true)
![ss1](https://github.com/melihyabas/Weather-Data-Backend/blob/main/databasecreation/ss4.PNG?raw=true)

Now you can run the project.


```

flask run

```
You could use Postman
