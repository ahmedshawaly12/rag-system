from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
from controlers import DataController, ProjectController, ProcessController
from models import ProjectModel, DataChucnkModel, DataChunckSchema, AssetModel, AssetSchema
import aiofiles
from models import ResponseSignal, AssetTypeEnum
from .schemes.data import ProcessRequest
import logging

ProjectModel
logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(prefix='/api/v1/data', tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload(request:Request , project_id: str, file: UploadFile, 
                 app_settings:Settings=Depends(get_settings)):


    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
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

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource = AssetSchema(
         asset_name= file_id, 
         asset_type= AssetTypeEnum.FILE.value, 
         asset_size=file.size, 
         asset_project_id= project.id, 
         )
    
    
    asset_rec = await asset_model.create_asset(asset=asset_resource)

    

    return JSONResponse(
        content={
            'signal': ResponseSignal.FILE_UPLOADED_SUCESSFULLY.value,
            'asset_detail': str(asset_rec.id)
            },
        
    )


@data_router.post('/process/{project_id}')
async def process_endpoint(request: Request, project_id: str, process_request:ProcessRequest):



    data_chunck_model = await DataChucnkModel.create_instance(db_client=request.app.db_client)

    

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset


    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)


    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(project_id=project.id, asset_name=process_request.file_id)

        if asset_record is None:
            return JSONResponse(
                content={'signal': ResponseSignal.FILE_ID_ERROR.value},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }

    else:
        asset_records = await asset_model.get_all_assets_by_project_id(
            project_id=project.id, 
            asset_type=AssetTypeEnum.FILE.value)

        project_files_ids = {asset_rec.id: asset_rec.asset_name for asset_rec in asset_records}


    if len(project_files_ids) == 0:
        return JSONResponse(
            content= {'signal': ResponseSignal.NO_FILES_ERROR.value},
            status_code = status.HTTP_400_BAD_REQUEST
        )


    process_controller = ProcessController(project_id)
    data_chunck_model = await DataChucnkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        _ = await data_chunck_model.remove_chunck_by_project_id(project_id=project.id)



    num_records = 0
    num_files = 0
    for asset_id, asset_name in project_files_ids.items():
             
        file_content = process_controller.get_file_content(asset_name)

        if file_content is None:
            logger.error(f"Error while processing {asset_name}")
            continue

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


        num_records += await data_chunck_model.insert_many_chuncks(chuncks=file_chuncks_records)
        num_files +=1


    return JSONResponse(content = {
        'signal': ResponseSignal.PROCESSING_SUCCESS.value,
        'num_records': num_records,
        'processed_files': num_files
        })



