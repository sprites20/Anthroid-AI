import requests
import json


url = "https://api.vectara.io/v1/upload?c=4239971555&o=2"
headers = {
    'x-api-key': 'zwt__LjU4zVE9TBF1tU4SbJ0rrjT1QWwI2sXXp4iGQ'
}

files = {
    "file": ('buildozer.spec', open('D:/pyfiles/newapp1/buildozer.spec', 'rb')),
    "doc_metadata": (None, json.dumps(metadata)),  # Replace with your metadata
}
response = requests.post(url, headers=headers, files=files)
print(response.text)