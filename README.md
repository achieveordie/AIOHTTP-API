# Asynchronous HTTP-API based on [FastAPI](https://fastapi.tiangolo.com) and [asyncpg](https://github.com/MagicStack/asyncpg).

An API for fast, asynchronous GET calls between
server (based on FastAPI) and PostgreSQL database 
(based on asyncpg driver), written in python.

## Table of Contents
1. [Introduction](#intro): Defining the problem
2. [Guiding Principles](#principles): Principles kept in mind when designing the solution
3. [Setting up](#setup): How to set up the API and tests 
4. [Details](#details): Details about individual files and working
5. [Conclusion](#conclusion): Scope of improvement


<a name="intro"></a>
### Introduction
#### Problem Statement
Develop an API endpoint which takes four query parameters
`date_from`, `date_to`, `origin` & `destination` and returns
a list with average prices for each day between `date_from` and 
`date_to` for location from `origin` to `destination`. Return `null` for days
on which there are less than 3 prices in total. Both locations can either be
a port code or a region slug.

### About the database
There is sql-dump provided in [rates.sql](/sql/rates.sql) that contains the database required for the project.
It contains three tables with the following information:
1. Ports
    - 5-character port code
    - Name of the port
    - Slug describing to which region the port belongs to
2. Regions
   - Slug of the region
   - Name of the region
   - Parent slug to which this region belongs to
3. Prices
    - Origin port_code
    - Destination port_code
    - The day for which the price is valid
    - Price in USD.

The interesting aspect of this database is how region-region
or port-region connectivity occurs. It can essentially be thought of in terms of a tree structure:
 - At the root, there are main regions that have no parent-slug.
 - Derived from the root are sub-regions that have main regions as parent.
 - At the leaf, the ports may either belong to root regions or any of sub-regions.

<a name="principles"></a>
### Guiding Principles
This project aims to demonstrate how DB-drivers can directly be used to connect to the web app,
as opposed to ORMs. The following principles were followed when making stack or design based decisions:
1. _Lightweight and self-contained_:

   Example: Usage of [`docker-compose`](https://docs.docker.com/compose/) to set up the containers, each of them
   being a derived image of compact `alpine`.

2. _Fast and asynchronous_:

    Example: Usage of ASGI over WSGI framework and DB drivers.

3. _Readability over DRY (for sql statements)_:

    Since this project involves writing direct [SQL queries](/src/app/api/sql.py), one has to choose
    whether they want to divide the query over f-strings, so they are not repeated or write them as
    a single string. I chose the latter since it provides far-better readability at the cost of few extra
    lines.

<a name="setup"></a>
### Setting up
There is a [`docker-compose`](/docker-compose.yml) file that is to be used to set up this project.
Please ensure you have Docker and Compose already installed.

There are two containers, one for the API and one for the DB. They can be set up directly, thanks to `docker-compose`,
I'll also show how to move into the running containers to run commands inside them as an option, useful for diagnosis.

#### Steps to set up and run the API:
1. Fork this repo and set it up on your local system. Change directory till command prompt points to the root
of the project.
2. Type `docker-compose up --build` to build the containers and wait till it shows that images have been built.
3. Open another command prompt and type `docker container ps` to check if both containers are running.
4. After confirming that both containers are running. You're ready to run the API.

#### Running the API locally on your host:
1. Open up your favorite browser and write a test it via `http://localhost:8002/rates?<your-query>`. Replace `<your-query>`
with your actual data. Eg:

```
http://localhost:8002/rates/?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=EETLL
``` 

#### Running the API inside the container hosting the web application:
1. In the command-prompt that was opened second (and used to check whether containers were running),
type the following command:

   ``` shell
   docker-compose exec -it web sh
   ```
   This interactively executes the `web` container via `bash`. Now you can look around in this container.

2. To run API, use `curl` (result shown to stdout) or `wget` (results stored in file). Eg:
   ``` shell
   curl http://localhost:8000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=china_south_main&destination=baltic_main
   ```
   
3. Type `exit` to get out of this container.

#### Checking out the container hosting the Database:
1. In the command-prompt that was opened second (and used to check whether containers were running),
type the following command:

   ``` shell
   docker-compose exec -it db psql -U postgres
   ```
   This interactively enters into the `db` container as `postgres` user.
2. Write relevant [commands](https://tomcam.github.io/postgres/) as per your wish to look around the database.
Eg: `\conninfo` to see information about the current PostgreSQL connection.
3. Type `exit` to get out of this container.

#### Running tests:
1. In the command-prompt that was opened second (and used to check whether containers were running),
type the following command:

   ``` shell
   docker-compose exec web sh python -m pytest .
   ```
   Wait to show 100% run and passed status. It should take within 5 seconds for completion.

#### Closing the running session:
It is very important to close the containers properly, or they'll keep running in the memory and eat up
your resources. To properly close the session:
1. In the first command prompt (the one that shows the logs), press `Ctrl+c` once to stop the containers graciously.
Press it again to force stop them.
2. Once out, type `docker-compose down --volumes` to destroy networks and volumes created. Doing this ensures that a new
volume is set up and populated with sql dump with every new session, avoiding erroneous stuff from previous session to leak
onto a new one.
3. Close the terminal.

<a name="details"></a>
### Details
This section is entirely for reference for someone who wants to know what each file is doing.
More information about each file is present in the first line.

Starting from the root:
1. [`sql/`](/sql) directory: contains the SQL dump.
   1. [`rates.sql`](/sql/rates.sql): the SQL dump.
2. [`src/`](/src) directory: contains all the source code.
   1. [`app/`](/src/app) directory: contains all API functionality.
      1. [`api/`](/src/app/api) directory: code for pydantic validators and sql queries.
      2. [`validate/`](/src/app/validate) directory: code for validation of inputs.
      3. [`__init__.py`](/src/app/__init__.py): initializing file for this package (empty).
      4. [`main.py`](/src/app/main.py): the starting and main file of execution. 
   2. [`tests/`](/src/tests) directory: contains all the test scripts.
      1. [`__init__.py`](/src/tests/__init__.py): initializing file for test directory (empty).
      2. [`manually_tested.txt`](/src/tests/manually_tested.txt): text file to contain most diverse examples.
      3. [`test_main.py`](/src/tests/test_main.py): test functionalities related to `main.py`.
      4. [`test_validate.py`](/src/tests/test_validate.py): test functionalities related to `validate` directory.
   3. [`Dockerfile`](/src/Dockerfile): To make the `web` container.
   4. [`requirements.txt`](/src/requirements.txt): Contains all versioned packages to build the virtual environment.
3. [`.gitignore`](/.gitignore): what directories and files to ignore from version control.
4. [`docker-compose.yml`](/docker-compose.yml): Compose file to build both the containers.
5. [`README.md`](/README.md): This file, gives info about the project.


<a name="conclusion"></a>
### Conclusion
There are various ways to extend and improve this project:
1. Using file-based password validation for DB than writing them inside `docker-compose.yml` for better
security.
2. Being mindful of possible SQL injections when extending to insert functionality.
3. Writing tests in form of cronjobs to run on actual database than monkeypatching it.
4. More validation and docs focus via pydantic models.
