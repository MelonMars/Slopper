import requests, base64
image = "Water bottle"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
data = {
    "prompt": "image",
    "steps": 5
}

print(data)
response = requests.post(url='http://127.0.0.1:7862/sdapi/v1/txt2img', json=data, headers=headers)
with open(image.replace(" ", "") + ".png", 'wb') as f:
    try:
        f.write(base64.b64decode(response.json()['images'][0]))
    except:
        print("Error: ", response.json())