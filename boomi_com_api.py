from requests import Session
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from utils import log_response

BASE_URL    = "https://api.boomi.com/api/rest/v1/"
JSON_TYPE   = "application/json"
XML_TYPE    = "application/xml"
MAX_WORKERS = 3

class BoomiAPI(Session):
    
    def __init__(self, id: str, username: str, password: str):
        super().__init__()
        self.auth     = (username, password)
        self.id       = id
        self.headers  = {"Content-Type" : JSON_TYPE, "Accept": JSON_TYPE}
        self.base_url = BASE_URL + id + "/"
    
    def request(self, method: str, endpoint: str, payload: str=None) -> dict:
        response = super().request(method, self.base_url + endpoint, data=payload)
        log_response(self.id, endpoint.split("/")[0], response)
        response.raise_for_status()
        return  response.json()
    
    def get(self, object: str, id: str) -> dict:
        return self.request("GET", f"{object}/{id}")
    
    def query(self, object: str, filter: dict=None) -> list[dict]:
        results = list()
        suffix = "/query"
        payload = json.dumps(dict(QueryFilter=dict(expression=filter))) if filter else None
        with tqdm(desc=f"{object:20}") as pbar:
            while True:
                response = self.request("POST", f"{object}{suffix}", payload)
                if "result" not in response:
                    break
                results += response["result"]
                pbar.update(len(response["result"]))
                if pbar.total != response["numberOfResults"]:
                    pbar.total = response["numberOfResults"]
                    pbar.refresh()
                if "queryToken" not in response:
                    break
                payload = response["queryToken"]
                suffix = "/queryMore"
            return results

    def multi_query(self, queries: dict) -> list[list[dict]]:
        return list(ThreadPoolExecutor(MAX_WORKERS).map(self.query, queries.keys(), queries.values()))