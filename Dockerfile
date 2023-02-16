FROM apache/airflow:slim-2.5.1-python3.9
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
         default-libmysqlclient-dev build-essential \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt