from fastapi import APIRouter, UploadFile, Depends
from helpers import Settings, get_settings
from controlers import DataController

data_router = APIRouter(prefix='/api/v1/data', tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload(project_id: str, file: UploadFile, app_settings:Settings=Depends(get_settings)):



    #Validate the file properties
    data_controller = DataController()

    is_validate, msg = data_controller.validate_upload_file(file)

    return {'is_validate': is_validate, 'message': msg}


