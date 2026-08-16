from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import DistanceMethodEnum

from models.db_schemes import RetrievedDocument
from qdrant_client import models, QdrantClient
from typing import List
import logging


class QdrantProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):

        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE

        elif distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)




    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None


    def is_collection_exist(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        # if self.is_collection_exist(collection_name=collection_name):
        return self.client.get_collection(collection_name=collection_name)


    
    def delete_collection(self, collection_name: str):
        if self.is_collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)


    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool=False):

        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection_exist(collection_name=collection_name):
            _ = self.client.create_collection(collection_name=collection_name, 
                                          vectors_config=models.VectorParams(
                                              size=embedding_size,
                                              distance=self.distance_method
                                          ))

            return True
        return False


    def insert_one(self, collection_name: str, text: str, vector: list, 
                   metadata: dict=None, record_id: str=None):

        if not self.is_collection_exist(collection_name=collection_name):

            self.logger.erro(f"Cannot insert a new record in a  non existing collection: {collection_name}")
            return False

        try:
            self.client.upload_points(
                collection_name=collection_name,
                points=[models.Record(
                    id=[record_id],
                    payload={'text': text, 'metadata': metadata},
                    vector=vector,
                    
                )]
            )

        except Exception as e:
            self.logger(f'Error while inserting batch {e}')
            return False

        return True



    def insert_many(self, collection_name: str, texts: list, vectors: list, 
                    metadatas: list=None, record_ids: list=None, batch_size:int=50):
        if not metadatas:
            metadatas = [None] * len(texts)

        if not record_ids:
            record_ids = [str(i) for i in range(len(texts))]

        for i in range(0, len(texts), batch_size):

            batch_metadata = metadatas[i: i+batch_size]
            batch_record_ids = record_ids[i: i+batch_size]
            batch_texts = texts[i: i+batch_size]
            batch_vectors = vectors[i: i+batch_size]

            batch_records = [models.Record(
                id=batch_record_ids[x], 
                vector=batch_vectors[x], 
                payload={'text': batch_texts[x], 'metadata': batch_metadata[x]}) for x in range(len(batch_texts))]


            try:
                self.client.upload_points(collection_name=collection_name, points=batch_records)

            except Exception as e:
                self.logger.error(f"Error while insert batch at collection {e}")
                return False

            return True



# points=[ScoredPoint(id=113, version=0, score=0.5635418064216707, payload={'text': 'Data Analytics Engineer with hands-on experience in building end-to-end analytics pipelines and', 'metadata': {'source': '/home/ahmed-shawaly/mini_rag_proj/src/assets/files/55/oxyi0afh1k98_test.txt'}}, vector=None, shard_key=None, order_value=None), ScoredPoint(id=115, version=0, score=0.328268406482054, payload={'text': 'foundation in ETL development, data transformation, dimensional modeling, and analytical reporting.', 'metadata': {'source': '/home/ahmed-shawaly/mini_rag_proj/src/assets/files/55/oxyi0afh1k98_test.txt'}}, vector=None, shard_key=None, order_value=None)]


    def search_by_vector(self, collection_name:  str, vector: list, limit: int):
        results = self.client.query_points(collection_name=collection_name, 
                                 query=vector, limit=limit).points


        if not results or len(results) == 0:
            return None
        


        return [RetrievedDocument(**{'text': result.payload['text'], 'score': result.score}) for result in results]

        