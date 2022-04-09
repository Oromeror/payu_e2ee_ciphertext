from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import app_payu_hub_e2ee_card
#from database import mysql
from settings import ENVIRONMENT

app = FastAPI()

if ENVIRONMENT == 'prod':
    origins = ['https://zapacommerce.web.app']
else:
    origins = ['https://zapacommerce-development.web.app', 'http://localhost:4200']

@app.get('/')
def read_root():
    return{"welcome":"API is working."}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# PayU Hub e2ee
app.include_router(app_payu_hub_e2ee_card, prefix='/api/payu-hub')

#@app.on_event('startup')
#def connect_db():
    #mysql.sql_conn = mysql.db_connection()