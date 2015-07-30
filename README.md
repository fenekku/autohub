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

Installation instructions go here.

## API Documentation

### Add new car

Add a new car with description.

    POST /api/add_car

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

