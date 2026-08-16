from .providers import QdrantProvider
from .VectorDBEnum import VectorDBEnum
from controlers import BaseController


class VectorDBProviderFactory:

    def __init__(self, config: dict):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider_name: str):
        if provider_name == VectorDBEnum.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTORDB_PATH)
            return QdrantProvider(db_path=db_path, 
                                  distance_method=self.config.VECTORDB_DISTANCE_METHOD)

        return None
        