# test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
import json
import urllib.parse


client = TestClient(app)

def url_encode(data):
    """ URL encode a string. """
    return urllib.parse.quote(data)

def double_url_encode(data):
    """ Double URL encode a string. """
    return urllib.parse.quote(urllib.parse.quote(data))

@pytest.mark.asyncio
async def test_post_user_create():
   
    init_data_raw = "user=%257B%2522id%2522%253A99281932%252C%2522first_name%2522%253A%2522Andrew%2522%252C%2522last_name%2522%253A%2522Rogue%2522%252C%2522username%2522%253A%2522rogue%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%257D&auth_date=1716922846&start_param=debug&chat_type=sender&chat_instance=8428209589180549439&hash=4e4fc271ee094311bc7e127c1a4a3437914e9188a33da7ee10fa1f6c6edd6ff8"


     # Define headers
    headers = {"Content-Type": "application/json"}

    response = client.post(
        "/api/users",
        headers=headers,
        json={"initDataRaw": init_data_raw}) 
    
    # Ensure the response status code is 200 OK
    assert response.status_code == 200
    
    # Get the JSON response
    response_json = response.json()

    # Check the response based on user existence
    if response_json.get("redirect") == "/choose-role":
        # Check response when creating a new user
        response_existing_user = client.post("/api/users", headers=headers, json={"initDataRaw": init_data_raw})
        assert response_existing_user.status_code == 200
        assert response_existing_user.json() == {"redirect": "/profile"}
    else:
        # Check the response structure
        assert "redirect" in response_json
        assert response_json["redirect"] == "/profile"
