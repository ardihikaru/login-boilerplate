# See https://unit.nginx.org/installation/#docker-images
# Build: `$ docker build -t ardihikaru/api-service:test .`
# Run: `$ docker run --rm -it --name fapi1 --env-file .env  --network host ardihikaru/api-service:test`
FROM nginx/unit:1.25.0-python3.9
MAINTAINER Muhammad Febrian Ardiansyah (ardihikaru3@gmail.com)

ENV PYTHONUNBUFFERED 1

# Nginx unit config and init.sh will be consumed at container startup.
COPY ./init.sh /docker-entrypoint.d/init.sh
COPY ./nginx-unit-config.json /docker-entrypoint.d/config.json
RUN chmod +x /docker-entrypoint.d/init.sh

# Build folder for our app, only stuff that matters copied.
RUN mkdir build
WORKDIR /build

COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .
COPY ./requirements-dev.txt .
COPY ./pyproject.toml .
COPY ./.env .

# Update, install requirements and then cleanup.
RUN apt update && apt install -y python3-pip                                  \
    && pip3 install -r requirements-dev.txt                                       \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list