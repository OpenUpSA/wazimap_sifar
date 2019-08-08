# Samson Institute for Ageing Research

Wazimap instance containing information about Older Adults in South Africa


## Docker Compose Route

1. Run Docker-Compose
```
docker-compose up
```
If this is the first time running it, it will build all the required images (wazimap-sifar and wazimap-postgres).

Once the builds are finished, the dumped sql tables will be imported. This will cause the wazimap_sifar container to fail initially since the database will still be importing the files and will not have started.

Once the import is complete, shut down docker-compose then bring it up again.

2. We now have to add some fixtures
```
docker exec -it wazimap-sifar python manage.py loaddata fixtures/census/wazimap_django_models.json
```

3. Add admin user
```
docker exec -it wazimap-sifar python manage.py createsuperuser
```

## Docker Build Route

If you want to build the images individually.

The are 2 images that you have to build

1. Postgres

```
docker build --tag=wazimap-postgres -f docker/db/Dockerfile .
```


2. Wazimap sifar application
```
docker build --tag=wazimap-sifar -f docker/web/Dockerfile .
```

3. Once complete you can run docker-compose
```
docker-compose up
```


## Local Development Route

1. clone the repo

2. ```cd wazimap_sifar```

3. ```virtualenv --no-site-packages env2```

4. ```source env2/bin/activate```

5. ```pip install -r requirements.txt```


### GDAL

If you are going to install gdal, there are a couple of things to configure first

5.1. Make sure you have installed gdal on your system including the development file, for debian based OS's

```apt install gdal-bin libgdal-dev```
	   
5.2. Get the system gdal version ```gdal-config version```

5.3. export some gdal header paths to the system environment

   ```export CPLUS_INCLUDE_PATH=/usr/include/gdal```
   
   ```export C_INCLUDE_PATH=/usr/include/gdal```
   
5.4. In the requirements.txt file make sure the gdal version matches the system version

5.5. ```pip install -r requirements.txt```
	   

6. Unzip the sql/census.zip and import the sql data

   ```cat sql/census/*.sql | psql -U wazimap_sifar -W wazimap_sifar```
   
   
7. Run django migrations

	```./manage.py migrate```
	
8. Import default data for django models

	```./manage.py loaddata fixtures/census/wazimap_django_models.json```

