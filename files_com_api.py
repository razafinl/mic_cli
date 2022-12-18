from requests import Session, Response
import logging
from utils import log_response

BASE_URL = "https://app.files.com/api/rest/v1/"
NEXT_HEADER = "X-Files-Cursor-Next"

# logger = logging.getLogger()

class FilesComAPI(Session):
    domain = "undefined"
    
    def __init__(self, api_key:str):
        super().__init__()
        self.auth   = (api_key,'x')
        self.domain = self.get("site")[0]["domain"].split(".")[0]
        self.params = dict(per_page=10000)
        
    def get(self, obj: str, params: dict=None) -> tuple[Response, dict]:
        response = super().get(BASE_URL + obj, params=params)
        log_response(self.domain, obj, response)
        # logger.debug(f"{self.domain} | GET {obj} | Completed in {response.elapsed.total_seconds()} second(s)")
        if response.status_code >= 300:
            response.raise_for_status()
        return  response.json(), response.headers
        
    def query(self, obj: str) -> list[dict]:
        result = list()
        params = dict()
        while True:
            response, headers = self.get(obj, params=params)
            result += response
            if NEXT_HEADER in headers:
                params["cursor"] = headers[NEXT_HEADER]
            else:
                break
        return result