from .db_schemes import AssetSchema
from .BaseDataModel import BaseDataModel
from .enum import DataBaseEnum
from bson.objectid import ObjectId



class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance


    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_ASSETS_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]
            for index in AssetSchema.get_indexes():
                await self.collection.create_index(index['key'], name=index['name'], unique=index['unique'])



    async def create_asset(self, asset: AssetSchema):
        
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset


    async def get_all_assets_by_project_id(self, project_id: ObjectId, asset_type: str):
        records = await self.collection.find(
            {'asset_project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id, 
             'asset_type': asset_type}
            ).to_list(length=None)

        return [AssetSchema(**doc) for doc in records]


    async def get_asset_record(self, asset_name: str, project_id: ObjectId):
        record = await self.collection.find_one({
            'asset_project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id,
            'asset_name': asset_name
        })

        if record:
            return AssetSchema(**record)

        return None

        
    
