from .BaseController import BaseController
from fastapi import UploadFile


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    def validate_upload_file(self, file: UploadFile):


        if file.content_type not in list(self.app_settings.FILE_ALLOWED_TYPES):
            return False, "FILE_TYPE_NOT_SUPPORTED"

        if file.size > self.size_scale * self.app_settings.FILE_MAX_SIZE:
            return False,  "FILE_SIZE_EXCEEDED"

        return True, "FILE_UPLOADED_SUCESSFULLY"

    