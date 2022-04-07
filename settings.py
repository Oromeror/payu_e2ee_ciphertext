import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

ENVIRONMENT = os.environ.get("ENVIRONMENT")
PAYMENTS_DATABASE = os.environ.get('DATABASE')

if ENVIRONMENT != 'prod':
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_HOST = os.environ.get('MYSQL_HOST')

else:
    MYSQL_USER = os.environ.get('MYSQLCONNSTR_MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQLCONNSTR_MYSQL_PASSWORD')
    MYSQL_HOST = os.environ.get('MYSQLCONNSTR_MYSQL_HOST')