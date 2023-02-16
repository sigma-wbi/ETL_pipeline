# Airflow with Docker Compose

## Requirements
- Docker Engine
- .env 파일

## .env 파일 예시
```
# path ./.env

# Airflow Core
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW_UID=0

# Backend DB
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS=False

# Airflow Init
_AIRFLOW_DB_UPGRADE=True
_AIRFLOW_WWW_USER_CREATE=True
_AIRFLOW_WWW_USER_USERNAME=airflowuser
_AIRFLOW_WWW_USER_PASSWORD=airflowpass
```

## 실행 방법
```
docker compose up -d
```

## 접속 방법 (예시)
http://127.0.0.1:8080/ 접속  
username & password는 .env 파일에 작성한 값 사용
```
_AIRFLOW_WWW_USER_USERNAME=airflowuser
_AIRFLOW_WWW_USER_PASSWORD=airflowpass
```