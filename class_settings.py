import json
import tempfile
import uuid

"""
    Файл настроек имеет следующий вид:
    {
    	"server": "mssqlserver",
	    "database": "dbname",
	    "login": "login",
	    "password": "password", 
        "ofd_login": "name",
        "ofd_password": "password",
        "ofd_token": "hex_array"
    }
"""


class Settings:
    def __init__(self, filename="ofd_request.json"):
        try:
            with open(filename, "r") as file:
                self.__settings = json.loads(file.read())
            self.__errors = False
        except Exception as E:
            self.__errors = True
            print(f"Исключительная ситуация: {E}")

    def param(self, param_name):
        return self.__settings.get(param_name, None)

    @property
    def errors(self):
        return self.__errors

    @property
    def new_id(self):
        return str(uuid.uuid4())

    @classmethod
    def random_file_name(cls, ext="tmp"):
        if tempfile.gettempdir()[:-1] == "\\":
            return tempfile.gettempdir() + str(uuid.uuid4()) + "." + ext
        else:
            return tempfile.gettempdir() + "\\" + str(uuid.uuid4()) + "." + ext

    @classmethod
    def random_file_name_local(cls, ext="dump"):
        return str(uuid.uuid4()) + "." + ext
