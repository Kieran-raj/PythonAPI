import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ENV = os.environ.get("ENV")
DEBUG = os.environ.get(("DEBUG"))
