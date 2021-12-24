import pytest
from api.app import create_app

testing_config = 'api.config.TestConfig'#

def test_heartbeat():
    """
    WHEN the '/heartbeat' endpoint is requested (GET)
    THEN check that the response is valid
    """
    test_app = create_app(testing_config)
    with test_app.test_client() as test_client:
        response = test_client.get('/expenses/heartbeat')
        assert response.status_code == 200
        assert b"API working" in response.data

def full_data_status_code_200():
    """
    WHEN the '/full_data' endpount is request (GET)
    THEN check that the response is valid
    """
    return True