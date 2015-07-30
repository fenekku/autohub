
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

def car_json_to_tuple(car_json):
    # Return car tuple from car json
    car_tuple = [None for _ in xrange(7)]
    car_tuple[0] = car_json["owner"]
    car_tuple[1] = car_json["name"]
    car_tuple[2] = car_json.get("brand", u"")
    if not isinstance(car_tuple[2], unicode):
        raise InvalidFieldError("brand")
    car_tuple[3] = car_json.get("year", -1)
    if not isinstance(car_tuple[3], int):
        raise InvalidFieldError("year")
    car_tuple[4] = car_json.get("engine", -1.0)
    if not isinstance(car_tuple[4], float):
        raise InvalidFieldError("engine")
    car_tuple[5] = car_json.get("description", u"")
    if not isinstance(car_tuple[5], unicode):
        raise InvalidFieldError("description")
    fn = car_json.get("picture", u"")
    if not isinstance(fn, unicode):
        raise InvalidFieldError("picture")
    fn = basename(fn)
    car_tuple[6] = fn

    return car_tuple


class InvalidJSONError(Exception):
    pass

class InvalidFieldError(Exception):
    pass

# Database Models
# eventually use Car object

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

    car_tuple = car_json_to_tuple(car_json)
    cursor.execute("""INSERT INTO cars (name, owner, brand, year,
                                        engine, description, picture)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""", car_tuple)
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

def update_car_in_db(car_id, car_dict, db):
    # Return tuple representing updated car
    cursor = db.cursor()
    cols = car_dict.keys()
    vals = car_dict.values()
    set_str = ", ".join("{}=?".format(key) for key in cols)
    cursor.execute("UPDATE cars SET {} WHERE id = ?".format(set_str),
                   vals + [car_id])
    db.commit()
    cursor.execute("SELECT * FROM cars WHERE id=?", car_id)
    return cursor.fetchone()

def delete_car_in_db(car_id, db):
    # Return if deletion was successful
    cursor = db.cursor()
    r = cursor.execute("DELETE FROM cars WHERE id = ?", car_id).rowcount
    return r == 1

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

@valid_request
def update_car(request):
    # Process an update car request
    # Ugly but more time better
    set_autohub_metadata(request)

    car_id = request.matchdict.get('id', "")
    car_json = {}
    if "owner" in request.json:
        car_json["owner"] = request.json["owner"]
        if not isinstance(car_json["owner"], unicode):
            raise InvalidFieldError("owner")
    if "name" in request.json:
        car_json["name"] = request.json["name"]
        if not isinstance(car_json["name"], unicode):
            raise InvalidFieldError("name")
    if "brand" in request.json:
        car_json["brand"] = request.json["brand"]
        if not isinstance(car_json["brand"], unicode):
            raise InvalidFieldError("brand")
    if "year" in request.json:
        car_json["year"] = request.json["year"]
        if not isinstance(car_json["year"], int):
            raise InvalidFieldError("year")
    if "engine" in request.json:
        car_json["engine"] = request.json["engine"]
        if not isinstance(car_json["engine"], float):
            raise InvalidFieldError("engine")
    if "description" in request.json:
        car_json["description"] = request.json["description"]
        if not isinstance(car_json["description"], unicode):
            raise InvalidFieldError("description")
    if "picture" in request.json:
        if not isinstance(request.json["picture"], unicode):
            raise InvalidFieldError("picture")
        car_json["picture"] = basename(request.json["picture"])

    car_tuple = update_car_in_db(car_id, car_json, get_db())

    if not car_tuple:
        json_response = {'error': 'Car not found'}
        request.response.status_int = 404
    else:
        json_response = car_tuple_to_json(car_tuple)

    return json_response

def delete_car(request):
    set_autohub_metadata(request)
    car_id = request.matchdict.get("id", "")
    if car_id:
        result = delete_car_in_db(car_id, get_db())
        if result:
            json_response = {'Message': 'Deleted car {}'.format(car_id)}
        else:
            request.response.status_int = 404
            json_response = {'error': 'Non-existing car'}
    else:
        request.response.status_int = 404
        json_response = {'error': 'Non-existing car'}
    return json_response

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

    config.add_route(UPDATE_CAR_ROUTE, CAR_ENDPOINT+"/{id}",
                     request_method='PUT')
    config.add_view(update_car,
                    route_name=UPDATE_CAR_ROUTE,
                    renderer='json')

    config.add_route(DELETE_CAR_ROUTE, CAR_ENDPOINT+"/{id}", request_method='DELETE')
    config.add_view(delete_car,
                    route_name=DELETE_CAR_ROUTE,
                    renderer='json')

    app = config.make_wsgi_app()

    return app

if __name__ == '__main__':
    app = main({})
    server = make_server('0.0.0.0', 6547, app) # real setup in reality
    print ('Starting up server on http://localhost:6547')
    server.serve_forever()