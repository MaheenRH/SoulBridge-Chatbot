import requests

url = "http://127.0.0.1:8000/chat"
data = {"message": "I feel a bit down today."}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Response:", response.json())
