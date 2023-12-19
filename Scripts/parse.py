import json

with open("output.json", "r") as file:
    jsonData = json.load(file)

data = json.dumps(jsonData["192.168.123.1"]["ports"], indent=2)
# Traversing the json file

print("Port: ", data)
