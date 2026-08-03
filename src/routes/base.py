from fastapi import APIRouter
from dotenv import load_dotenv
import os

load_dotenv('.env')

app_name = os.getenv('APP_NAME')
app_version = os.getenv('APP_VERSION')

base_router = APIRouter(prefix='/api/v1', tags=['api_v1'])

@base_router.get('/')
async def welcome():
    return {'APP_NAME': app_name, 'APP_VERSION': app_version}