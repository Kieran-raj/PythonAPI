from os import environ
from dotenv import load_dotenv

load_dotenv()


class ProdConfig:
    """Get environmental variables"""
    database_username = environ.get("DATABASE_USERNAME")
    database_password = environ.get("DATABASE_PASSWORD")
    database_ip = environ.get("DATABASE_IP")
    database_port = environ.get("DATABASE_PORT")
    database = environ.get("DATABASE_NAME")

    """Set Flask config variables"""
    ENV = 'production'
    DEBUG = False
    TESTING = False

    """Set SQL_ALCHEMY Variables"""
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{database_username}:{database_password}@{database_ip}:{database_port}/{database}_prod"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestConfig:
    """Set Flask config variables"""
    ENV = 'testing'
    DEBUG = False
    TESTING = True

    """Set SQL_ALCHEMY Variables"""
    # SQLALCHEMY_DATABASE_URI = "sqlite:///D:\\Projects\\PythonAPI\\api\\tests\\expenses\\testing_database\\expenses_test.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/kieran/PythonAPI/api/tests/expenses/testing_database/expenses_test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevConfig:
    """Get environmental variables"""
    database_username = environ.get("DATABASE_USERNAME")
    database_password = environ.get("DATABASE_PASSWORD")
    database_ip = environ.get("DATABASE_IP")
    database_port = environ.get("DATABASE_PORT")
    database = environ.get("DATABASE_NAME")

    """Set Flask config variables"""
    ENV = 'development'
    DEBUG = True
    TESTING = True

    """Set SQL_ALCHEMY Variables"""
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{database_username}:{database_password}@{database_ip}:{database_port}/{database}_dev"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
