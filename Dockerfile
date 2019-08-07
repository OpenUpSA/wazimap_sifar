FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt install -y gdal-bin libgdal-dev
RUN apt install -y python-pip git

ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

RUN mkdir /sifar
WORKDIR /sifar

COPY . /sifar

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
