import pytest
from src.app.dark_factory.ui.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_status_endpoint(client):
    rv = client.get('/api/status')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == "ONLINE"

def test_metrics_endpoint(client):
    rv = client.get('/api/metrics')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'power_w' in json_data
    assert 'temp_c' in json_data

def test_alerts_endpoint(client):
    rv = client.get('/api/alerts')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) > 0
