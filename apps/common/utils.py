import requests
from django.conf import settings

def upload_to_imgbb(image_file):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": settings.IMGBB_API_KEY,
    }
    files = {
        "image": image_file.read(),
    }
    response = requests.post(url, data=payload, files=files)
    data = response.json()

    if data["success"]:
        return data["data"]["url"]
    return None