# Airflow를 사용한 ETL PipeLine

## 배포
Airflow webserver :


## 프로젝트 소개
Airflow, RDS, EC2, S3를 사용하여 ETL PipeLine 구축 및 자동화


## ETL 상세 내용

* Extract 
Dummy data를 RDS에 저장하고 이 데이터를 기반으로 생성된 Log data를 가져옴

* Transform 
Log data의 길이 및 용량을 줄이기 위해 필요없는 문자 제거 및 딕셔너리 형식 사용

* Load
S3에 적재시 gz형식으로 한번 더 압축 및 날짜와 시간별로 파티셔닝 후 저장


## 📚Stack

![badge](https://img.shields.io/badge/AmazonRDS-527FFF?style=flat-square&logo=AmazonRDS&logoColor=white)
![badge](https://img.shields.io/badge/AmazonS3-009639?style=flat-square&logo=AmazonS3&logoColor=white)
![badge](https://img.shields.io/badge/AmazonEC2-990099?style=flat-square&logo=AmazonEC2&logoColor=white)
![badge](https://img.shields.io/badge/Airflow-FF9900?style=flat-square&logo=apache-airflow&logoColor=white)



## Installation
> 우선적으로 docker가 필요합니다. Airflow는 리눅스 기반환경에서 구동하였습니다. 

* 리눅스 환경은 EC2, 로컬환경, WSL등 원하는대로 구축 하시면됩니다.


### Docker 설치 
참고 자료 : https://docs.docker.com/engine/install/ubuntu/  


1. 도커를 설치 후 우리의 레포지토리에서 클론해옵니다.
```python
$ git clone https://github.com/cp2-2team/cp2_ETL_pipeline.git
```


2. 해당 디렉토리안에 .env파일을 작성합니다. 내용은 아래와 같습니다. [] 안은 수정해주세요  
```python
# Airflow Core
# AIRFLOW__CORE__FERNET_KEY=[FERNET_KEY]
AIRFLOW__CORE__EXECUTOR=LocalExecutor
# AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW_UID=0

# Backend DB
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS=False

# Airflow Init
_AIRFLOW_DB_UPGRADE=True
_AIRFLOW_WWW_USER_CREATE=True
_AIRFLOW_WWW_USER_USERNAME=airflow

# REST API에서 암호화 할 때 사용했던 key를 업로드
key=[Fernet key]

aws_access_key_id = [S3 access key]
aws_secret_access_key = [S3 secret access key]

bucket_name=[your s3 bucket name]
mysql_conn_id=[your RDS name]

# 아래는 dummy data 를 생성하기 위한 정보입니다. 
uesrname=[your api Admin id]
password=[your api Admin password]
```


3. 확장자 .yml 이 있는 디렉토리로 들어가 해당 명령어를 실행합니다.  
```python
$ docker compose up -d --build 
```

4. airflow 설정
IP+8080포트로 접속 후 Admin 페이지에서 connections 클릭 후 add a new record 클릭

* RDS DB 설정 
아래와 같이 입력 후 저장
![image](https://user-images.githubusercontent.com/109950265/219989632-f68ee40f-00a0-489c-bda5-7a4cb58d1176.png)

* S3 설정 
아래와 같이 입력 후 저장
![image](https://user-images.githubusercontent.com/109950265/219989581-88ffeacf-322e-4219-8b04-4f07cfa0dc20.png)

5. dag 다시 실행

6. S3 접속 
데이터 gz형식으로 날짜별로 파티셔닝 되는 것을 볼 수 있습니다.  


## 추가내용
해당 dag가 어떻게 돌아가는지 확인하고 싶다면 IP+8080포트로 접속하시면 됩니다.

Airflow를 EC2안에서 활용한다면 메모리 용량에 서버가 불안정할 수 있습니다. 

일반적인 경우 약 4GB의 메모리를 필요로 합니다.

임시방편으로 사용하지 않는 저장소를 메모리로 변환하여 사용할 수 있습니다.

아래는 t2.micro(1GB 메모리 제공)에서 적용한 코드입니다.   

* 단, 지정하는 블록크기는 인스턴스에서 사용 가능한 메모리보다 작아야합니다.

```python
# 만약 memory exhausted 에러가 발생한다면 bs=64M으로 조정해보세요
$ sudo dd if=/dev/zero of=/swapfile bs=128M count=32

# 스왑 파일의 읽기 및 쓰기 권한을 업데이트
$ sudo chmod 600 /swapfile

# Linux 스왑 영역을 설정
$ sudo mkswap /swapfile

# 스왑 공간에 스왑 파일을 추가
$ sudo swapon /swapfile

# 프로시저가 성공적인지 확인
$ sudo swapon -s

# /etc/fstab 파일을 편집하여 부팅 시 스왑 파일을 시작 후 아래의 코드를 추가
$ sudo vi /etc/fstab

/swapfile swap swap defaults 0 0
```
