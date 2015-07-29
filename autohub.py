
from os.path import basename

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config


#Globals
ADD_CAR_ROUTE = 'add_car'
LIST_CAR_ROUTE = 'list_car'
UPDATE_CAR_ROUTE = 'update_car'
DELETE_CAR_ROUTE = 'delete_car'

next_id = 0
picture_path = "http://localhost:6547/cars/{id}/{filename}"

# Helper functions

def set_autohub_metadata(request):
    # Modify `request` to have the AutoHub-specific metadata
    request.response.headerlist.append(("X-AutoHub-Media-Type", "autohub.v1"))


# Main API Endpoints

def add_car(request):
    # Process a request to add a car
    global next_id

    set_autohub_metadata(request)

    # No persistence for now
    json_response = request.json
    fn = basename(json_response["picture"])
    json_response["id"] = next_id
    json_response["picture"] = picture_path.format(id=json_response["id"],
                                                   filename=fn)
    next_id += 1

    return json_response

# def list_car(request):
#     set_autohub_metadata(request)
#     return {'name': 'Hello View'}

# def update_car(request):
#     set_autohub_metadata(request)
#     return {'name': 'Hello View'}

# def delete_car(request):
#     set_autohub_metadata(request)
#     return {'name': 'Hello View'}


# Running the server

def main():
    config = Configurator()

    config.add_route(ADD_CAR_ROUTE, '/api/add_car')
    config.add_view(add_car,
                    route_name=ADD_CAR_ROUTE,
                    renderer='json')

    # config.add_route(LIST_CAR_ROUTE, '/api/cars')
    # config.add_view(list_car,
    #                 route_name=LIST_CAR_ROUTE,
    #                 renderer='json')

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
    app = main()
    server = make_server('0.0.0.0', 6547, app) # real setup in reality
    print ('Starting up server on http://localhost:6547')
    server.serve_forever()