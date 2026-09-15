#!/bin/sh
set -eu

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
CREATE DATABASE harborai_test;
GRANT ALL PRIVILEGES ON DATABASE harborai_test TO harborai;
SQL
