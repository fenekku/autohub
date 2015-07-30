#AutoHub


*Renseignons-nous mieux, ensemble, sur les autos.*

API pour échanger des informations sur des autos.

Given this is a public API, the documentation and URLs will be in the
modern day "lingua franca", English.

## Example Usage

In one terminal:

    > python autohub.py
    Starting up server on http://localhost:6547


In another:

    curl -l http://localhost:6547/api/cars/1
    OUTPUT HERE

## Installation

Install pyramid

    pip install -r requirements.txt

## Run locally

    python autohub.py

## API Documentation

### Add new car

Add a new car with name and owner (at least).

    POST /api/cars

**Input**

| Parameter Name |  Type  |                 Description               |
|----------------|:------:|:------------------------------------------|
| owner          | string |                *Required* The car's owner |
| name           | string |                 *Required* The car's name |
| brand          | string |              The car's brand. Default: "" |
| year           | number | The car's year of production. Default: -1 |
| engine         | number |    The motor's engine in L. Default: -1.0 |
| description    | string |       The car's description. Default: ""  |
| picture        | string |  URL to a picture of the car. Default: "" |

Each `owner` and `name` pair must be unique.

**Output**

A typical car json:

| Parameter Name |  Type  |                Description               |
|----------------|:------:|:-----------------------------------------|
| id             | string |                                Unique id |
| owner          | string |                          The car's owner |
| name           | string |                           The car's name |
| brand          | string |                          The car's brand |
| year           | number |             The car's year of production |
| engine         | number |                  The motor's engine in L |
| description    | string |                    The car's description |
| picture        | string |              URL to a picture of the car |

### List all cars

List all cars.

    GET /api/cars

**Output**

A JSON list of typical car json

### List a car

List a car by `id`.

    GET /api/cars/{id}

**Output**

The corresponding typical car json.

### Update a car

Update a car by `id`.

    PUT /api/cars/{id}

**Input**

| Parameter Name |  Type  |                 Description               |
|----------------|:------:|:------------------------------------------|
| owner          | string |                *Required* The car's owner |
| name           | string |                 *Required* The car's name |
| brand          | string |              The car's brand. Default: "" |
| year           | number | The car's year of production. Default: -1 |
| engine         | number |    The motor's engine in L. Default: -1.0 |
| description    | string |       The car's description. Default: ""  |
| picture        | string |  URL to a picture of the car. Default: "" |

**Output**

The corresponding typical car json.

### Delete a car

Delete a car by `id`.

    DELETE /api/cars/{id}

**Output**

| Parameter Name |  Type  |                 Description               |
|----------------|:------:|:------------------------------------------|
| Message        | string |                          Deleted car {id} |


### If there is an error

**Output**

| Parameter Name |  Type  |                 Description               |
|----------------|:------:|:------------------------------------------|
| error          | string |                             Error message |


## Testing

Install `nose`:

    pip install nose

Run tests very simply:

    $ nosetests


## Notes

First dabbling with Pyramid: so I didn't have time to use their niceties.
Some refactorings could be done: have a Car object and better validations.
Structure and layers kept to a minimum because the project is small.
