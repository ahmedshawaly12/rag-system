from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
from controlers import DataController, ProjectController, ProcessController
from models import ProjectModel, DataChucnkModel, DataChunckSchema
import aiofiles
from models import ResponseSignal
from .schemes.data import ProcessRequest
import logging

ProjectModel
logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(prefix='/api/v1/data', tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload(request:Request , project_id: str, file: UploadFile, 
                 app_settings:Settings=Depends(get_settings)):


    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id)


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


@data_router.post('/process/{project_id}')
async def process_endpoint(request: Request, project_id: str, process_request:ProcessRequest):


    prject_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await prject_model.get_or_create_project(project_id=project_id)

    data_chunck_model = await DataChucnkModel.create_instance(db_client=request.app.db_client)

    process_controller = ProcessController(project_id)

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    file_id = process_request.file_id
    do_reset = process_request.do_reset

    file_content = process_controller.get_file_content(file_id)

    file_chuncks = process_controller.process_file_content(
        file_content=file_content, 
        chunk_size=chunk_size, 
        chunk_overlap= overlap_size
        )

    if file_chuncks is None or len(file_chuncks) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=ResponseSignal.PROCESSING_FAILED.value)

    file_chuncks_records = [DataChunckSchema(chunck_text= chunck.page_content ,
                      chunck_metadata=chunck.metadata, 
                      chunck_order=i+1, 
                      chunck_project_id=project.id) for i, chunck in enumerate(file_chuncks)]


    data_chunck_model = await DataChucnkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        _ = await data_chunck_model.remove_chunck_by_project_id(project_id=project.id)

    num_records = await data_chunck_model.insert_many_chuncks(chuncks=file_chuncks_records)


    return JSONResponse(content = {
        'signal': ResponseSignal.PROCESSING_SUCCESS.value,
        'num_records': num_records
        })



