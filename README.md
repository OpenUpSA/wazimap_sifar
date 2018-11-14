# Samson Institute for Ageing Research

Wazimap instance containing information about senior citizens in South Africa


## Local Development

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

