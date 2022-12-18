from os.path import dirname, realpath, join, splitext
from os import makedirs
import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from yaml import safe_load
from itertools import groupby

from InquirerPy import inquirer
from  InquirerPy.base.control import Choice
import logging
from requests import Response

def init_log(scriptname: str) -> None:
    # Create Log dir if it does not exists
    script_dir = dirname(realpath(scriptname))
    log_dir = join(script_dir, "log")
    makedirs(log_dir, exist_ok=True)
    # Configure logging
    log_file = splitext(scriptname)[0] + ".log"
    logging.basicConfig(
        handlers=[RotatingFileHandler(join(log_dir, log_file), maxBytes=100000, backupCount=10)],
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
def read_yaml(filename: str) -> dict:
    with open(filename, "r") as input_file:
        return safe_load(input_file)
    
def group_by(array: list[dict], key: str, multi: bool=True) -> dict:
    return {k:list(grp) if multi else list(grp)[0] for k,grp in groupby(array, lambda row: row[key])}
    
def inquire(label: str, choices: Any, multi: bool=False) -> Any:
    return inquirer.fuzzy(
        message     = "Select " + label,
        choices     = [Choice(v,k) for k,v in choices.items()] if isinstance(choices, dict) else choices,
        multiselect = multi
    ).execute()
    
def log_response(instance: str, resource: str, response: Response) -> None:
    logging.getLogger().debug(" | ".join(map(str,[
        instance,
        response.request.method,
        resource,
        response.status_code,
        response.elapsed.total_seconds()
    ])))