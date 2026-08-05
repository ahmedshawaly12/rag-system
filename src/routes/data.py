from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
from controlers import DataController, ProjectController
import aiofiles
from models import ResponseSignal
import logging


logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(prefix='/api/v1/data', tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload(project_id: str, file: UploadFile, 
                 app_settings:Settings=Depends(get_settings)):


    #Validate the file properties
    data_controller = DataController()

    is_validate, result_signal= data_controller.validate_upload_file(file)

    if not is_validate:
        return JSONResponse(content={"signal":result_signal}, 
                            status_code=status.HTTP_400_BAD_REQUEST)


 
    project_dir = ProjectController().get_project_path(project_id)

    file_path, file_id = data_controller.get_unique_file_path(
        org_file_name=file.filename,
        project_id=project_id)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunck := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunck)
    except Exception as e:
        logger.error(f"Error while uploadig file: {e}")
        return JSONResponse(
            content={'signal': ResponseSignal.FILE_UPLOADED_FAILED.value},
            status_code=status.HTTP_400_BAD_REQUEST
        )


    return JSONResponse(
        content={
            'signal': ResponseSignal.FILE_UPLOADED_SUCESSFULLY.value,
            'file_id': file_id
            },
        
    )



