import datetime
import random

from flask import Flask, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from datetime import *
from flask import request, Flask, jsonify
import pytz
from datetime import date, timedelta as td, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "Your_secret_string"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
CORS(app)

conn = psycopg2.connect( # database connection with credentials
    host="localhost",
    database="teaNetworks",
    user="postgres",
    password="1")


@app.route('/')
def home():  # just a try to see if program is running
    passhash = generate_password_hash("password")
    print(passhash)

    return jsonify(passhash)

@app.route('/login', methods=['POST'])
def login():
    _json = request.json    # get username and password from json body
    _username = _json['username']
    _password = _json['password']

    print(_password)    # print them
    print(_username)
    if _username and _password:
        # check user exists
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # create cursor to execute sql

        sql = "SELECT * FROM useraccount WHERE username=%s"
        sql_where = (_username,)

        cursor.execute(sql,sql_where)
        row = cursor.fetchone()

        if row:
            username = row['username'] # get user name and password from the row
            password = row['password']
            if check_password_hash(password,_password):
                session['username'] = username
                cursor.close()

                userJson = { # convert user info to a json format
                    "username": row['username'],
                    "password": row['password'],
                    "name": row['name'],
                    "role": row['role']
                }
                response = jsonify({'message':'Logged in successfully', 'user info':userJson})
                response.status_code = 200
                return response
            else: # wrong password
                response = jsonify({'message':'Bad Request - invalid password'})
                response.status_code = 400
                return response
        else: # return error if user does not exist in database
            msg = "Bad Request - This user does not exist: {}".format(_username)
            response = jsonify({'message':msg})
            response.status_code = 400
            return response

    else: # return an error if credentials are invalif
        response = jsonify({'message': 'Bad Request - invalid credentials'})
        response.status_code = 400
        return response

@app.route('/user', methods=['DELETE'])
def userDelete(): # deletes a user
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'DELETE':
        id = request.args.get('user_id') # get uuid format user_id

        sql = "SELECT * FROM useraccount WHERE user_id::text=%s"
        sql_id =   (id,)
        cursor.execute(sql,sql_id)  # get user row if it exists
        row = cursor.fetchone()

        if (row):
            sql = "DELETE FROM useraccount WHERE user_id::text=%s"
            sql_id = (id,)  # execute delete comment and remove the user from table
            cursor.execute(sql, sql_id)
            conn.commit()

            userJson = {
                "username": row['username'],
                "password": row['password'],
                "name": row['name'],    # return user info in json format
                "role": row['role']
            }
            response = jsonify({'message':'The user successfully deleted.','user info':userJson})
            response.status_code = 200
            return response
        else: # return an error if the user with related user id does not exist
            return jsonify({'message':'Related user does not exist.'})

@app.route('/user', methods=['GET'])
def userGet(): # returns the user for given user id
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    id = request.args.get('user_id')
    sql = "SELECT * FROM useraccount WHERE user_id::text=%s"
    sql_id = (id,)   # select the user

    cursor.execute(sql, sql_id)
    row = cursor.fetchone()

    if(row): # if there is a user with this id, return its information in json format
        userJson = {
            "username": row['username'],
            "password": row['password'],
            "name": row['name'],
            "role": row['role']
        }
        return userJson
    else: # return an error if there is no user with this user id
        return jsonify({"message":"The user does not exist."})

@app.route('/user', methods=['POST','PUT'])
def userPutPost(): # create a user or update user information
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    _json = request.json    # get user info from json body
    _username = _json['username']
    _password = _json['password']
    _name = _json['name']
    _role = _json['role']
    _role = str(_role)
    if _role!='end' and _role!='admin': # role must be end or admin
        return jsonify({'message':'role must be \'end\' or \'admin\''})

    if _username and _password and _name and _role: # if credentials are valid
        id = request.args.get('user_id') # get user id if it is given

        if (id): # PUT or POST request for updating data
            sql = "SELECT * FROM useraccount WHERE user_id::text=%s"
            sql_where = (id,)

            cursor.execute(sql,sql_where) # get related user with this id
            row = cursor.fetchone()

            if(row): # Update the user information
                _password = generate_password_hash(_password)
                sql = "UPDATE useraccount SET username=\'{}\', password=\'{}\', name=\'{}\', role=\'{}\' WHERE user_id=\'{}\';".format(
                    _username, _password, _name, _role, id )

                cursor.execute(sql)
                conn.commit() # execute update command

                userJson = { # return updated user information as json format
                    "username": _username,
                    "password": _password,
                    "name": _name,
                    "role": _role
                }
                response = jsonify({'message':'User successfully updated.','user info':userJson})
                response.status_code=200 # return successfully created message
                return response
            else:
                response = jsonify({'message': 'This user does not exist!'})
                response.status_code = 400 # related user does not exist, it can not be updated
                return response
        elif request.method == 'POST': # create a user section
            sql = "SELECT * FROM useraccount WHERE username=%s"
            sql_where = (_username,) # check if there is a user with this user name

            cursor.execute(sql,sql_where)
            row = cursor.fetchone()

            if(row): # if there is a user with this username, return error
                response = jsonify({'message': 'This user has already exist!'})
                response.status_code = 400
                return response
            else: # there is no user with this database, create it
                password = generate_password_hash(_password)
                # hash the password
                sql = "INSERT INTO useraccount (username, password, name, role) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')"\
                    .format(_username,password,_name,_role)

                cursor.execute(sql) # execute the insert commang
                conn.commit()

                response = jsonify({'message': 'New user created.'})
                response.status_code = 200 # user successfully created. Return this
                return response
        else:
            resp = jsonify({'message': 'Bad Request - invalid user id'})
            resp.status_code = 400 # invalid user id while updating user information
            return resp
    else:
        resp = jsonify({'message': 'Bad Request - invalid credendtials'})
        resp.status_code = 400 # invalid credentials
        return resp




@app.route('/weather', methods=['GET'])
def weather(): # filters the weatherdata table and gets the related data
    _json = request.json
    print(_json)
    _condition = ""
    _timeBegin = "" # first create parameters as empty string
    _timeEnd = ""   # because one or more of them may not be in parameters
    _temperature = ""
    _location = ""

    paramCount = 0 # temporary variable to create correct string
    if('condition' in _json):
        _condition = _json['condition'] # rainy, sunny
        _condition = "condition=\'{}\'".format(_condition)
        paramCount = paramCount+1 # increase it to show the other if statements, there is a condition parameter


    if('timeBegin' in _json): # start time
        _timeBegin = _json['timeBegin']
        _timeBegin = "timestamp>=\'{}\'".format(_timeBegin)
        if paramCount>0: # if there is a condition parameter add an and to string
            _timeBegin = "and "+_timeBegin
        paramCount = paramCount+1

    if('timeEnd' in _json): # end time
        _timeEnd = _json['timeEnd']
        _timeEnd = "timestamp<=\'{}\'".format(_timeEnd)
        if paramCount>0: # if there is a condition parameter or more, add an and to string
            _timeEnd = "and "+_timeEnd
        paramCount = paramCount+1


    if('temperature' in _json):
        _temperature = _json['temperature'] # 30, 24
        _temperature = "temperature={}".format(_temperature)
        if paramCount>0: # if there is a condition parameter or more, add an and to string
            _temperature = "and "+_temperature
        paramCount = paramCount+1

    if('location' in _json):
        _location = _json['location'] #loc1,
        _location = "location=\'{}\'".format(_location)
        if paramCount>0:  # if there is a condition parameter or more, add an and to string
            _location = "and "+_location


    sql = "SELECT * FROM weatherdata where {} {} {} {}"\
        .format(_condition, _timeBegin, _timeEnd, _temperature, _location)
    # filter table with parameters
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print('\n-------SQL--------\n')
    print(sql)
    cursor.execute(sql) # execute command
    row = cursor.fetchall() # get all results

    return jsonify(row) # return results

def createWeatherData(): # Creates more than millions of random data for weatherdata table
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    conditions = ["sunny", "cloudy", "rainy", "windy", "snowy"]
    location = "location"

    eastern = pytz.timezone('Europe/Istanbul')

    d1 = eastern.localize(datetime(2022, 1, 1, 0, 0, 0)) # select all dates in 2022
    d2 = eastern.localize(datetime(2022, 12, 31, 23, 59, 59))

    count = 0
    for i in range(115): # for 115 different location
        while(d1<d2): # for 365 days

            sql = "INSERT INTO weatherdata (condition, timestamp, temperature, location) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')" \
                .format(random.choice(conditions), d1.isoformat(), random.randint(-10,50), "loc"+str(i))

            # randomly generated data
            cursor.execute(sql)
            conn.commit()

            count = count+1
            if(count%100000==0):
                print(count)
            d1 = eastern.normalize(d1 + td(hours=1))
        d1 = eastern.localize(datetime(2022, 1, 1, 0, 0, 0))

    print(count)

if __name__ == '__main__':
    app.run(debug=True)


#createWeatherData()