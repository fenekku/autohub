
import collections
import os
from os.path import basename
import sqlite3

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config


#Globals
DB_NAME = "autohub.db"
__DB = None
ADD_CAR_ROUTE = 'add_car'
LIST_CAR_ROUTE = 'list_car'
LIST_CARS_ROUTE = 'list_cars'
UPDATE_CAR_ROUTE = 'update_car'
DELETE_CAR_ROUTE = 'delete_car'

next_id = 0
picture_path = "http://localhost:6547/cars/{id}/{filename}"

CAR_ENDPOINT = '/api/cars'

# Helper exceptions

class InvalidJSONError(Exception):
    pass

class InvalidFieldError(Exception):
    pass

# Database Models

def create_db(name):
    # Create database - this is manual eventually we can use an ORM
    create = not os.path.exists(name)
    autohub_db = sqlite3.connect(name)

    if create:
        cursor = autohub_db.cursor()
        # Create the necessary tables
        cursor.execute('''CREATE TABLE cars
                          (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                          name TEXT NOT NULL,
                          owner TEXT NOT NULL,
                          brand TEXT,
                          year INTEGER,
                          engine REAL,
                          description TEXT,
                          picture TEXT,
                          UNIQUE(name, owner))''') #picture as URL for simplicity
        #No users now so no real need for another table yet
        autohub_db.commit()

    return autohub_db

def get_db():
    # Singleton-ish pattern for access to database
    global __DB

    if not os.path.exists(DB_NAME):
        __DB = create_db(DB_NAME)
    elif not __DB:
        __DB = sqlite3.connect(DB_NAME)
    else:
        pass
    return __DB

def delete_db(name):
    if os.path.exists(name):
        if DB_NAME == name:
            db = get_db()
            db.close()
        os.remove(name)

def add_car_to_db(car_json, db):
    # Add `car_json` json object to database `db`
    # Eventually use ORM with niceties
    # Return the id of the inserted car in the database
    cursor = db.cursor()

    car = [None for _ in xrange(7)]
    car[0] = car_json["owner"]
    car[1] = car_json["name"]
    car[2] = car_json.get("brand", u"")
    if not isinstance(car[2], unicode):
        raise InvalidFieldError("brand")
    car[3] = car_json.get("year", -1)
    if not isinstance(car[3], int):
        raise InvalidFieldError("year")
    car[4] = car_json.get("engine", -1.0)
    if not isinstance(car[4], float):
        raise InvalidFieldError("engine")
    car[5] = car_json.get("description", u"")
    if not isinstance(car[5], unicode):
        raise InvalidFieldError("description")
    fn = car_json.get("picture", u"")
    if not isinstance(fn, unicode):
        raise InvalidFieldError("picture")
    fn = basename(fn)
    car[6] = fn
    cursor.execute("""INSERT INTO cars (name, owner, brand, year,
                                        engine, description, picture)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""", car)
    car_id = cursor.lastrowid
    db.commit()

    return car_id

def list_car_in_db(car_id, db):
    # Return iterator of tuples representing cars
    # Eventually return iterator of car objects
    cursor = db.cursor()
    if not car_id:
        cursor.execute("SELECT * FROM cars ORDER BY id")
        return cursor
    else:
        cursor.execute("SELECT * FROM cars WHERE id=?", car_id)
        return cursor.fetchone()

# Helper functions and classes

def set_autohub_metadata(request):
    # Modify `request` to have the AutoHub-specific metadata
    request.response.headerlist.append(("X-AutoHub-Media-Type", "autohub.v1"))

def valid_request(route_func):
    # Decorator returning error response if invalid request
    def __validated(request):
        try:
            assert request.content_type == 'application/json'
            return route_func(request)
        except AssertionError as ae:
            request.response.status = '400 Bad Request'
            return {"error": "Body should be JSON"}
        except InvalidJSONError as ije:
            request.response.status = '400 Bad Request'
            return {"error": "Problems parsing JSON"}
        except KeyError as ke:
            request.response.status = '400 Bad Request'
            return {"error": "Missing field", "field": ke.message}
        except InvalidFieldError as ife:
            request.response.status = '400 Bad Request'
            return {"error": "Invalid field format", "field": ife.message}
        except sqlite3.IntegrityError as ie:
            request.response.status = '400 Bad Request'
            return {"error": "Already existing car"}
        except Exception as e:
            request.response.status_int = 500
            import traceback
            traceback.print_exc() #print to log - eventually real logger
            return {"error": "Something potentially terrible happened!"}

    return __validated

def car_tuple_to_json(car_tuple):
    # Return json object representing car from the `car_tuple` tuple
    # ORM with more time and reality
    json_car = {}
    json_car["id"] = car_tuple[0]
    json_car["owner"] = car_tuple[1]
    json_car["name"] = car_tuple[2]
    json_car["brand"] = car_tuple[3]
    json_car["year"] = car_tuple[4]
    json_car["engine"] = car_tuple[5]
    json_car["description"] = car_tuple[6]
    fn = car_tuple[7]
    fn = picture_path.format(id=car_tuple[0], filename=fn) if fn else ""
    json_car["picture"] = fn

    return json_car

# Main API Endpoints

@valid_request
def add_car(request):
    # Process a request to add a car

    set_autohub_metadata(request)

    # Invalid json is returned as a unicode string
    # Valid json is returned as a dict
    if isinstance(request.json, unicode):
        raise InvalidJSONError()

    # Simple persistence for now
    car_id = add_car_to_db(request.json, get_db())

    json_response = {}
    json_response["id"] = car_id
    json_response["owner"] = request.json["owner"]
    json_response["name"] = request.json["name"]
    json_response["brand"] = request.json.get("brand", "")
    json_response["year"] = request.json.get("year", -1)
    json_response["engine"] = request.json.get("engine", -1)
    json_response["description"] = request.json.get("description", "")
    fn = basename(request.json.get("picture", ""))
    fn = picture_path.format(id=car_id, filename=fn) if fn else ""
    json_response["picture"] = fn

    return json_response

def list_car(request):
    # Process a request to list cars or a specific car.
    # Eventually paginate in the API

    set_autohub_metadata(request)

    car_id = request.matchdict.get('id', "")
    cars = list_car_in_db(car_id, get_db())
    if isinstance(cars, tuple):
        json_response = car_tuple_to_json(cars)
    elif isinstance(cars, collections.Iterable):
        json_response = [car_tuple_to_json(car) for car in cars]
    else:
        json_response = {'error': 'Car not found'}
        request.response.status_int = 404

    return json_response

# def update_car(request):
#     set_autohub_metadata(request)
#     return {'name': 'Hello View'}

# def delete_car(request):
#     set_autohub_metadata(request)
#     return {'name': 'Hello View'}


# Running the server

def main(settings):
    # Return the app object. `settings` is a dict of parameters
    global DB_NAME
    config = Configurator()

    DB_NAME = settings.get("DB_NAME", DB_NAME)

    config.add_route(ADD_CAR_ROUTE, CAR_ENDPOINT, request_method='POST')
    config.add_view(add_car,
                    route_name=ADD_CAR_ROUTE,
                    renderer='json')

    config.add_route(LIST_CARS_ROUTE, CAR_ENDPOINT, request_method='GET')
    config.add_view(list_car,
                    route_name=LIST_CARS_ROUTE,
                    renderer='json')

    config.add_route(LIST_CAR_ROUTE, CAR_ENDPOINT+"/{id}",
                     request_method='GET')
    config.add_view(list_car,
                    route_name=LIST_CAR_ROUTE,
                    renderer='json')

    # config.add_route(UPDATE_CAR_ROUTE, '/api/update_car')
    # config.add_view(update_car,
    #                 route_name=UPDATE_CAR_ROUTE,
    #                 renderer='json')

    # config.add_route(DELETE_CAR_ROUTE, '/api/delete_car')
    # config.add_view(delete_car,
    #                 route_name=DELETE_CAR_ROUTE,
    #                 renderer='json')

    app = config.make_wsgi_app()

    return app

if __name__ == '__main__':
    app = main({})
    server = make_server('0.0.0.0', 6547, app) # real setup in reality
    print ('Starting up server on http://localhost:6547')
    server.serve_forever()