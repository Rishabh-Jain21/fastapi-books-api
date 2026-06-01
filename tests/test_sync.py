# This file contains a synchronous way to test the sync endpoints and database connection. It is for learning purposes and is not used in the actual test suite which uses asynchronous tests with httpx and pytest.

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
client = TestClient(app)


@app.get("/sync")
def read_sync():
    return {"message": "hello world"}


def test_sync_endpoint():
    response = client.get("/sync")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}
