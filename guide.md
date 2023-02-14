# Airflow 설치

## 기본 설치
```
# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME=~/airflow

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.5.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# The Standalone command will initialise the database, make a user,
# and start all components for you.
airflow standalone

# Visit localhost:8080 in the browser and use the admin account details
# shown on the terminal to login.
# Enable the example_bash_operator dag in the home page
```

Short Version
```
export AIRFLOW_HOME=~/airflow
AIRFLOW_VERSION=2.5.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

## 설정 파일 수정
airflow.cfg 파일 수정
```
executor = LocalExecutor
load_examples = False
```


## MySQL 연결
MySQL 플러그인 설치
```
pip install apache-airflow[mysql]
```
airflow.cfg 파일 수정
```
[database]
mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
```

## 추가 패키지 설치
```
pip install -r requirements.txt
```

## AWS S3 설정
~/.aws 파일 수정
```
~/.aws/config

[default]
region=ap-northeast-2
```
```
~/.aws/credentials

[default]
aws_access_key_id = <my_access_key>
```

## 최초 실행
```
airflow db init

airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org

airflow webserver --port 8080

airflow scheduler
```