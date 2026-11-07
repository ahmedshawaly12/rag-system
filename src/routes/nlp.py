from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from .schemes.nlp import PushRequst, SearchRequest

from models import ProjectModel, DataChucnkModel

from controlers import NLPController

from models.enum import ResponseSignal



nlp_router = APIRouter(
    prefix='/api/v1/nlp/index',
    tags=['api_v1', 'nlp']
)


@nlp_router.post('/push/{project_id}')
async def index_project(request: Request, project_id: str, push_request: PushRequst = PushRequst()):


    print("welcome to push request")

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id)

    print("project_detail", project.project_id)


    data_chunck_model = await DataChucnkModel.create_instance(db_client=request.app.db_client)

    print("before nlp controller")


    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client)


    print("after nlp controller")

    page_num = 1
    idx = 0
    has_records =True

    inserted_items_counts = 0


    print("first done")

    

    while has_records:
        page_chunck = await data_chunck_model.get_chuncks_by_project_id(project_id=project.id,  
                                                                        page_num=page_num)

        print(f"page_chunck {page_num} getted successfult")

        if len(page_chunck):                                                      
            page_num+=1


        if not page_chunck or len(page_chunck) == 0:
            has_records == False
            break

        chunck_ids  = list(range(idx, idx + len(page_chunck)))
        idx = idx+len(page_chunck)




        is_inserted = nlp_controller.index_to_vector_db(project=project, 
                                          chuncks=page_chunck, 
                                          chunck_ids=chunck_ids, 
                                          do_reset=push_request.do_reset)

        print("is_inserted: ", is_inserted)

        if not is_inserted:
            return JSONResponse(
                content={'signal': ResponseSignal.INSERTED_INTO_VECTORDB_ERROR.value},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        inserted_items_counts += len(page_chunck)


    return JSONResponse(
        content={
            'signal': ResponseSignal.INSERTED_INTO_VECTOR_DB_SUCCESS.value,
            'inserted_items_count': inserted_items_counts
        }
    )



@nlp_router.get('/info/{project_id}')
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)


    project = await project_model.get_or_create_project(project_id=project_id)


    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client)


    try:
        collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    except Exception as e:
        return JSONResponse( 
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {'signal': ResponseSignal.VECTORDB_COLLECTION_NOT_EXIST.value})


    return JSONResponse(
        content= {
            'signal': ResponseSignal.VECTORDB_COLLECTION_INFO_RETRIEVED.value,
            'collection_info': collection_info
            }

    )




@nlp_router.post('/search/{project_id}')
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)



    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client)

    if not nlp_controller.check_collection_exist(project=project):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST ,
            content={
                'signal': ResponseSignal.VECTORDB_COLLECTION_NOT_EXIST.value,
            }
            )


    results = nlp_controller.search_vectordb_collection(project=project, 
                                              text=search_request.text, 
                                              limit=search_request.limit)


    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'signal': ResponseSignal.VECTORDB_SEARCH_ERROR.value}
        )

    return JSONResponse(
        content={
            'signal': ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            'results': [result.dict() for result in results]
        }
    )








    


    



    

        

        
        


    











    



