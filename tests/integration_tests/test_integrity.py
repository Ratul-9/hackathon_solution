import requests
import json

# The port is 5477 as per your Docker requirements
URL = "http://localhost:5477/blackrock/challenge/v1/returns:nps"

def test_full_pipeline():
    payload = {
        "age": 20,
        "wage": 60000,
        "inflation": 5.0,
        "q": [{"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59", "fixed": 100}],
        "p": [{"start": "2023-06-01 00:00:00", "end": "2023-06-30 23:59:59", "amount": 50}],
        "k": [],
        "transactions": [
            {"date": "2023-06-15 12:00:00", "amount": 450} # Remanent 50 + Q 100 + P 50 = 200
        ]
    }

    print("Sending Request to Docker Engine...")
    response = requests.post(URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Investment Value: {data.get('finalValue')}")
    else:
        print(f"❌ Failed! Status: {response.status_code}, Error: {response.text}")

if __name__ == "__main__":
    test_full_pipeline()