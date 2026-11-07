from .BaseController import BaseController

# from models import ProjectModel
from models.db_schemes import ProjectSchema, DataChunckSchema
from typing import List

from stores.llm.LLMEnum import DocumentTypeEnum
import json

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()


        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client


    def create_collection_name(self, project_id:str):
        return f"collection_{project_id}".strip()

    def check_collection_exist(self, project: ProjectSchema):
        collection_name = self.create_collection_name(project_id=project.project_id)

        return self.vectordb_client.is_collection_exist(collection_name)

    def get_vector_db_collection_info(self, project: ProjectSchema):
        collection_name = self.create_collection_name(project.project_id)

        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )


    def index_to_vector_db(self, project: ProjectSchema,chuncks: List[DataChunckSchema], 
                           chunck_ids:List[int] , do_reset:bool= True):

        # Step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)


        #step2: manage items
        texts = [chunck.chunck_text for chunck in chuncks]
        metadatas = [chunck.chunck_metadata for chunck in chuncks]
        vectors = self.embedding_client.embed_text(
                text=texts, 
                document_type=DocumentTypeEnum.DOCUMENT.value
                )

        #step3: create collection if not exist
        _ = self.vectordb_client.create_collection(collection_name=collection_name, 
                                               embedding_size=self.embedding_client.embedding_size, 
                                               do_reset=do_reset)

        #step4 insert into vectorDB

        _ = self.vectordb_client.insert_many(collection_name= collection_name, 
                                         texts=texts, 
                                         vectors=vectors, 
                                         metadatas=metadatas, 
                                         record_ids=chunck_ids 
                                         )
        

        return True


    def search_vectordb_collection(self, project: ProjectSchema, text: str, limit: int=10):

        collection_name = self.create_collection_name(project_id=project.project_id)

        encoded_text = self.embedding_client.embed_text(text=text, 
                                                        document_type=DocumentTypeEnum.QUERY.value)[0]


        if not encoded_text or len(encoded_text)==0:
            return False


        retrieve_chuncks = self.vectordb_client.search_by_vector(collection_name=collection_name, 
                                              vector=encoded_text,
                                              limit=limit
                                              )

        if not retrieve_chuncks:
            return False


        return retrieve_chuncks

        



    

        







