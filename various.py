import json

with open("bot_config.json") as file:
    file = json.load(file)
    print(file)
    file = json.dumps(file)

print(type(file))

# with open("bot_config.json", "w") as file2:
#     json.dump(file, file2)
