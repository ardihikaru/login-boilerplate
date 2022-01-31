[![Build Status](https://app.travis-ci.com/ardihikaru/login-boilerplate.svg?branch=main)](https://app.travis-ci.com/ardihikaru/login-boilerplate)

# login-boilerplate
A complete login application
- Docker image: [https://hub.docker.com/repository/docker/ardihikaru/login-boilerplate](https://hub.docker.com/repository/docker/ardihikaru/login-boilerplate)

## Requirements
- Python >= v3.8
- // TBD

## Github projects
There will be three github projects for this Login App:
- [Api Service](https://github.com/ardihikaru/login-boilerplate) (This repo)
- Email Publisher (TBD)
- ReactJS App for Frontend (TBD)
    
## Architecture design
- Initial architecture design to implement the Login Application
![Login App Figure](https://lh3.googleusercontent.com/pw/AM-JKLVfcUagF7W-4ykKhFafkInqPZuUKhTlatnZpS6nPXG1Ll9pslJdAUtKTKMhMgOpFPTc63Y0pj8Tb5--zmMI9AQaRKiA5rrwT91_ADL99UvzPB4ch_iVwSyR9o2lLk3z4HyOqVl6qA1mY6oB7nOQCv9o=w1109-h948-no?authuser=0)

## Database schema
- Simple schema for table `user`
![User Table Figure](https://lh3.googleusercontent.com/pw/AM-JKLVswqnAT6iUSDh3vlzbZ-ukzvs1fxjxYuRT3IGkiTAqGU3Ayt4ntcHKzgtKoAKmI74hj5kiwiWTh2Mt88zXvXQ3tpEHHkqfydlLjS93LxY-RdS65Qt9fDDiG1q_WtBNVn-adztPemGiUd0KgHW7-BH8=w664-h544-no?authuser=0)

## Implementation roadmap
I will implement the system step-by-step as follows:
1. Prepare the core backend framework; In this case I used [FastAPI boilerplate](https://github.com/tiangolo/full-stack-fastapi-postgresql) 
    from the official.
    - **FYI**: For simplier usage, I ended up using [This template](https://github.com/rafsaf/minimal-fastapi-postgres-template) 
        which simplified the official's with more updated packages. 
2. // TBD

## How to use
- Local Deployment (Tested with **Ubuntu 20.04**)
    - Prepare the environment for local deployment:
        - Install `venv`: `$ sudo apt-get install python3-venv`
        - Create python environment: `$ python3 -m venv venv`
        - Activate: `$ . venv/bin/activate` or `$ . venv/bin/activate.fish` (for [Fish Shell](https://github.com/fish-shell/fish-shell))
        - Upgrade pip: `$ pip install --upgrade pip`
        - Install `poetry`: `$ pip install poetry`
        - Install all requirements with poetry: `$ poetry install`
        - Alembic initialization (**OPTIONAL**): `$ alembic revision --autogenerate -m "initialization"`
            - This script will create a python file in `alembic/versions/*.py`
            - **FYI**: By default. I have prepared the file `2022_01_28_1243_initialization__868253e3f0c7.py`
                inside the `alembic/versions`.
        - Once this file generates we are ready for database migration,
            Run following command: `$ alembic upgrade head`
        - Run initialized data `$ bash init.sh`
            - This will create a superuser data that can be used to login.
            - Created user: 
                ```
                email = example@example.com
                pass  = OdLknKQJMUwuhpAVHvRC 
                ```
        - Now, you are ready to run the service. :)
    - Run the database with compose: `$ docker-compose -f docker-compose-db-only.yml --env-file .env.compose up -d --remove-orphans`
        - Here I use a docker-compose for the database to simplify the deployment. :)
        - To stop, run: `$ docker-compose -f docker-compose-db-only.yml --env-file .env.compose down`
    - Run api-service: `$ uvicorn app.main:app --reload`
    - Open on the browser: [http://localhost:8000](http://localhost:8000)
- Docker-compose
    - Run compose: `$ docker-compose --env-file .env.compose up -d --remove-orphans`
        - **FYI**: You can add `--build` on the end of the script to enforce the build in every execution
    - Open on the browser: [http://localhost:8001](http://localhost:8001)
- Accessing database via PGAdmin
    - Open PGAdmin in your favorite browser: `http://localhost:5050/`
    - Use any terminal and get the Internal IP of your deployed posgresql
        - First, inspect the docker network detail: `$ docker network inspect loginapp_database`
            - Find `Containers` and locate the IP (=`IPv4Address`) of your `login_postgresdb` service
                ``` 
                [
                    {
                        "Name": "loginapp_database",
                        ...
                        "Containers": {
                            ...
                            "a8747105a949cadeeace7f296f112ca3deb60d9ff2e43c4676170c8957de16a9": {
                                "Name": "login_postgresdb",
                                "EndpointID": "296a5ba37862f6e8ccc3d5cfdaff957559e3191f0b311d5406e5e161bf950f02",
                                "MacAddress": "02:42:c0:a8:50:02",
                                "IPv4Address": "192.168.80.2/20",
                                "IPv6Address": ""
                            },
                            ...
                        },
                        ...
                    }
                ]
                ```
            - In my case, the IP that I am looking for is `192.168.80.2`
            - Why not `localhost`? Of couse! Since they are communicating privately inside the docker network. ;)
        - Now, back to the browser and `Add New Server`
        - In the `General` tab, you can define any name, e.g., `myserver`
        - Then, go to `Connection` tab, and put following information:
            - `Hostname/Address` put your `IPv4Address` you found before, which is `192.168.80.2` for my case
            - `Port` put `5432`; Remember that it uses the **INTERNAL PORT**, not the exposed network, dude. ;)
            - `Maintainance database` put `default_db`
            - `Username` put `rDGJeEDqAz`
            - `Password` put `XsPQhCoEfOQZueDjsILetLDUvbvSxAMnrVtgVZpmdcSssUgbvs`
        - Finally, press the `Save` button!
    - **ALTERNATIVE**: As some devs prefer using a terminal, use this commands: 
        - Connecting to db:`$ psql -h localhost -d default_db -U rDGJeEDqAz -p 5387`
            - **FYI**: You are accessing the database from outside the terminal, so you use an EXPOSED PORT,
                which is `5387`.
        - Then, it will ask for your password, and put `XsPQhCoEfOQZueDjsILetLDUvbvSxAMnrVtgVZpmdcSssUgbvs`
    