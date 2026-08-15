from fastapi import FastAPI
from routes import base_router, data_router
from pymongo import AsyncMongoClient
from helpers import get_settings
from contextlib import asynccontextmanager
from .stores.llm import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):

    settings = get_settings()
    app.mongo_conn = AsyncMongoClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(config=settings)

    # generation_client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMDEDDING_MODEL_SIZE)
    

    yield

    await app.mongo_conn.close()


app = FastAPI(lifespan=lifespan)



app.include_router(base_router)

app.include_router(data_router)




