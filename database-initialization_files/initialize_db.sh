#!/bin/bash
echo "CREATE ROLE dekker_lab WITH LOGIN PASSWORD 'CHYYTS14#';" | psql
echo "create database clims_db;" | psql
echo "GRANT ALL PRIVILEGES ON DATABASE clims_db TO dekker_lab;" | psql
cat /db_backups/initial.sql.txt | psql clims_db
