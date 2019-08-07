FROM postgres:9.4

COPY sql/census/ /docker-entrypoint-initdb.d/
COPY sql/senior_citizens/ /docker-entrypoint-initdb.d/
COPY sql/extensions/ /docker-entrypoint-initdb.d/
