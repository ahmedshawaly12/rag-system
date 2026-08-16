from .BaseDataModel import BaseDataModel
from .enum import DataBaseEnum
from .db_schemes import DataChunckSchema
from bson.objectid import ObjectId
from pymongo import InsertOne

class DataChucnkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNCK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_CHUNCK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNCK_NAME.value]

            for index in DataChunckSchema.get_indexes():
                await self.collection.create_index(index['key'], name=index['name'], unique = index['unique'])



    async def create_chunck(self, chunck:DataChunckSchema):
        result = await self.collection.insert_one(chunck.model_dump(by_alias=True, exclude_unset=True))

        chunck.id = result.inserted_id
        return chunck

    async def get_chunck(self, chunck_id: str):
        chunck = await self.collection.find_one({"_id": ObjectId(chunck_id)})

        if chunck is None:
            return None

        return DataChunckSchema(**chunck)


    async def insert_many_chuncks(self, chuncks: list, batch_size:int=100):

        for i in range(0, len(chuncks), batch_size):
            batch = chuncks[i: i+batch_size]

            operations = [InsertOne(doc.model_dump(by_alias=True, exclude_unset=True)) for doc in batch]

            await self.collection.bulk_write(operations)

        return len(chuncks)

    async def remove_chunck_by_project_id(self, project_id: str):

        res = await self.collection.delete_many({'chunck_project_id': project_id})

        return res.deleted_count


    async def get_chuncks_by_project_id(self, project_id: ObjectId , page_num:int=1, page_size: int=50):

        
        results = await self.collection.find(
            {'chunck_project_id': project_id}
            ).skip((page_num-1) * page_size).limit(page_size).to_list(length=None)

        return [DataChunckSchema(**doc) for doc in results]



