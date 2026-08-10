from .BaseDataModel import BaseDataModel
from .enum import DataBaseEnum
from .db_schemes import ProjectSchema

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project: ProjectSchema):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_or_create_project(self, project_id: str):
        result = await self.collection.find_one({'project_id': project_id})

        if result is None:
            project = ProjectSchema(project_id=project_id)
            project = await self.create_project(project=project)
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




    
