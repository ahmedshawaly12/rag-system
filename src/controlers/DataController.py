from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    def validate_upload_file(self, file: UploadFile):


        if file.content_type not in list(self.app_settings.FILE_ALLOWED_TYPES):
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.size_scale * self.app_settings.FILE_MAX_SIZE:
            return False,  ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_UPLOADED_SUCESSFULLY.value


    def get_unique_file_path(self, org_file_name:str, project_id):

        random_key = self.generate_random_string()
        cleaned_file_name = self.get_clean_file_name(org_file_name)

        proj_dir_name = ProjectController().get_project_path(project_id)

        new_file_path = os.path.join(proj_dir_name, random_key+ '_' +cleaned_file_name)


        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(proj_dir_name, random_key+ '_' +cleaned_file_name)


        return new_file_path, random_key+ '_' +cleaned_file_name






    def get_clean_file_name(self, org_file_name:str):

        cleaned_f_name = re.sub(r'[^\w.]', '', org_file_name.strip())

        cleaned_f_name = cleaned_f_name.replace(' ', '_')

        return cleaned_f_name





    