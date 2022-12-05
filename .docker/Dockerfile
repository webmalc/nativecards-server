FROM python:3.7

RUN apt update && apt install -y python-dev libc-dev gettext sqlite3 libsqlite3-dev libpq-dev binutils libproj-dev gdal-bin

WORKDIR /usr/src/app
COPY ./requirements_dev.txt ./
COPY ./setup.py ./
COPY ./README.md ./
RUN pip install --no-cache-dir -r requirements_dev.txt
RUN pip install -e .
RUN pip install --no-cache-dir uwsgi whitenoise
COPY uwsgi.ini /etc/uwsgi.ini
RUN apt update && apt -y --no-install-recommends install fish