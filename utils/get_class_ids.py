import json

with open("notes.json", "r") as fin:
    dct = json.load(fin)
    for dct_ in dct["categories"]:
        print(str(dct_["id"]) + ": " + dct_["name"])

