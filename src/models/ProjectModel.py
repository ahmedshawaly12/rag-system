from .BaseDataModel import BaseDataModel
from .enum import DataBaseEnum
from .db_schemes import ProjectSchema

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance


    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

            indexes = ProjectSchema.get_indexes()

            for index in indexes:
                await self.collection.create_index(index['key'], name=index['name'], unique=index['unique'])



    async def create_project(self, project: ProjectSchema):
        print("inside create method: ",project)
        print("inside created with dump: ",project.model_dump(by_alias=True, exclude_unset=True))
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        print('result after insert: ', result)
        project.id = result.inserted_id
        return project

    async def get_or_create_project(self, project_id: str):
        result = await self.collection.find_one({'project_id': project_id})

        if result is None:
            project = ProjectSchema(project_id=project_id)
            print('not exist project: ', project)
            project = await self.create_project(project=project)
            print('inserted successfully')
            return project

        return ProjectSchema(**result)

    async def get_all_projects(self, page_number:int=1, page_size:int=10):

        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size

        if total_documents % page_size > 0:
            total_pages +=1

        cursor = self.collection.find().skip((page_number - 1) * page_size).limit(page_size)

        projects = []

        async for doc in cursor:
            projects.append(ProjectSchema(**doc))

        return projects, total_pages




    
