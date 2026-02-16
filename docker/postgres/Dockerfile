FROM postgres:15-alpine

# Copy the schema into the init directory
COPY database/schema.sql /docker-entrypoint-initdb.d/01-schema.sql

EXPOSE 5432
