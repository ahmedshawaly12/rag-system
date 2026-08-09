from fastapi import FastAPI
from routes import base_router, data_router
from pymongo import AsyncMongoClient
from helpers import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    settings = get_settings()
    app.mongo_conn = AsyncMongoClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    yield

    await app.mongo_conn.close()


app = FastAPI(lifespan=lifespan)



app.include_router(base_router)

app.include_router(data_router)




