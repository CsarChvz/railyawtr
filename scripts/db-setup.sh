#!/bin/sh

export PGUSER='postgres'

psql -c 'CREATE DATABASE chop_dev'

psql chop_dev -c 'CREATE EXTENSION IF NOT EXISTS \'uuid-ossp\';'

psql chop_dev -c 'CREATE EXTENSION IF NOT EXISTS vector;'
