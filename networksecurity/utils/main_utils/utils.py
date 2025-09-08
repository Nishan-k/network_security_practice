import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys
import numpy as np
import pickle
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score




def read_yaml_file(file_path:str) -> dict:
    """
    Responsible for reading the YAML file.
    """
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(file_path:str, content:object, replace:bool=False) -> None:
    """
    Responsible for writing the YAML File:
    """
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def read_data(file_path: str) -> pd.DataFrame:
    try:
        logging.info(f"Reading data from: {file_path}")
        return pd.read_csv(file_path)
    except Exception as e:
        raise NetworkSecurityException(e, sys)