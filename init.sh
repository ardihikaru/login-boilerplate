#!/bin/bash

echo "Run migrations"
alembic upgrade head

echo "Create initial data in DB"
python -m app.db.initial_data
