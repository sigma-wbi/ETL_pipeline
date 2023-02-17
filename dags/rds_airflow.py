from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os
import json
import string
import boto3
import requests
import random
import gzip


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'rds_airflow',
    default_args=default_args,
    # schedule_interval='0 0 * * *', # 하루 자정 마다
    schedule_interval='*/5 * * * *', # 5분마다
    # schedule_interval='*/2 * * * *', # 2분마다
    catchup=False
)

# url dict
url_dict ={"/api/common/user/" : 1,
        "/api/common/sigup/" : 2,
        "/api/common/token/" : 3,
        "/api/common/token/refresh/" : 4,
        "/api/common/token/verify/" : 5,
        "/api/board/questions/" : 6,
        "/api/board/answers/" : 7,
        "/api/log/logs/" : 8,
        "/api/statistic/gender/common/" : 9,
        "/api/statistic/age/common/" : 10,
        "/api/statistic/gender/board/" : 11,
        "/api/statistic/age/board/question/" : 12,
        "/api/statistic/age/board/answer/" : 13,
        "/api/statistic/usetime/common/" : 14}

# CURD dict
curd_dict ={"GET" : 1, "POST": 2, "PUT":3,"DELETE": 4}
base_url = 'https://cp2de.duckdns.org/api/'

aws_questions = ['How can I create an S3 bucket?', 'What is an EC2 instance?', 'How do I set up an RDS database?']
etl_questions = ['What is ETL?', 'How can I extract data from a database?', 'What are some ETL tools?']
airflow_questions = ['What is Airflow?', 'How can I create a DAG?', 'What are some Airflow operators?']

aws_contents = ['Amazon S3 is a scalable object storage service', 'Amazon EC2 is a web service that provides resizable compute capacity', 'Amazon RDS makes it easy to set up, operate, and scale a relational database in the cloud']
etl_contents = ['ETL stands for Extract, Transform, and Load', 'You can extract data from a database using SQL', 'Some popular ETL tools include Apache NiFi, Talend, and AWS Glue']
airflow_contents = ['Airflow is an open-source platform to programmatically author, schedule, and monitor workflows', 'You can create a DAG using Python code', 'Some popular Airflow operators include BashOperator, PythonOperator, and PostgresOperator']

def create_dummy_data(**kwargs):
    
    username= os.environ.get('username')
    password= os.environ.get('password')
    
    payload = {'username': username, 'password': password}
    r = requests.post(base_url+'common/token/', data=payload)
    token = json.loads(r.text)
    access = token.get('access')
    
    headers = {'Authorization': 'Bearer '+access}
    for i in range(10):
        if i % 3 == 0:
            subject = random.choice(aws_questions)
            content = random.choice(aws_contents)
        elif i % 3 == 1:
            subject = random.choice(etl_questions)
            content = random.choice(etl_contents)
        else:
            subject = random.choice(airflow_questions)
            content = random.choice(airflow_contents)

        data = {'subject': subject, 'content': content}
        requests.post(base_url+'board/questions/', headers=headers, data=data)
    
    
def extract_data_from_mysql(**kwargs):
    mysql_hook = MySqlHook(mysql_conn_id='mysql_rds')
    execution_date = kwargs.get('execution_date') + timedelta(hours=9)# airflow에서 작업의 마지막 실행 날짜/ 9시간 더해줘야함
    execution_time = execution_date.strftime('%s') # epoch time으로 변경
    execution_time = int(execution_time)
    
    sql = "SELECT * FROM log_log WHERE time >= {}".format(execution_time)
    df = mysql_hook.get_pandas_df(sql)
    json_data = df.to_dict(orient='records')
    
    key= os.environ.get('key')
    fernet = Fernet(key)

    result = []
    for log in json_data:
        encrypted = log['data'].encode('utf8') # 토큰값때문에 인코딩해줘야함
        decrypted = fernet.decrypt(encrypted).decode('utf8')
        
        json_decry = json.loads(decrypted.replace("'", "\"")) # json 형식은 ' -> "가 되야함
        
        # CURD 압축
        json_decry['method'] = curd_dict[json_decry['method']]

        # url 압축
        json_decry['url'] = url_dict[json_decry['url']]

        # created date 압축
        json_decry['created'] = json_decry['created'].translate(str.maketrans('','',string.punctuation)).replace(' ','')

        result.append(json_decry)

    return result

def load_to_s3(**kwargs):
    result = kwargs['ti'].xcom_pull(task_ids='extract_data_task') #앞의 함수의 리턴값을 가져옴
    aws_access = os.environ.get('aws_access_key_id')
    aws_secret = os.environ.get('aws_secret_access_key')
    # kwargs['ti']는 실행 중인 현재 작업의 TaskInstance 개체를 의미함 / 상태, 실행 날짜 및 기타 메타데이터를 포함하여 작업 인스턴스에 대한 정보가 있다.
    s3 = boto3.resource('s3', aws_access_key_id =aws_access, aws_secret_access_key =aws_secret)
    # kwargs['ti']는 실행 중인 현재 작업의 TaskInstance 개체를 의미함 / 상태, 실행 날짜 및 기타 메타데이터를 포함하여 작업 인스턴스에 대한 정보가 있다.
    bucket_name = 'cp2s3'
    current_time = datetime.now().strftime("%Y-%m-%dT%H-%M-%S") # 날짜별 새로운 로그데이터 파일
    partition_key = datetime.now().strftime("%Y-%m-%d") # 파티션키 
    partition_key2 = datetime.now().strftime("%H")
    
    file_name = f"{current_time}.json.gz"
    
    # 압축
    with gzip.open(file_name, 'wb') as f:
        f.write(json.dumps(result).encode('utf-8'))

    # 압축파일 업로드 + 데이터 파티셔닝
    s3.Bucket(bucket_name).upload_file(file_name, f"{partition_key}/{partition_key2}/{file_name}")


create_dummy_data_task = PythonOperator(
    task_id='create_dummy_data_task',
    python_callable=create_dummy_data,
    dag=dag,
    provide_context=True,
)

extract_data_task = PythonOperator(
    task_id='extract_data_task',
    python_callable=extract_data_from_mysql,
    dag=dag,
    provide_context=True, 
)

load_data_task = PythonOperator(
    task_id='load_data_task',
    python_callable=load_to_s3,
    dag=dag,
    provide_context=True,
)

create_dummy_data_task >> extract_data_task >> load_data_task