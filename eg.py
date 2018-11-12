from lib import entre_guillemets as EG
import json

def load_settings():
    with open('./settings.json') as data:
        settings = json.load(data)
    return settings

if __name__ == "__main__":
    settings = load_settings()
    eg = EG.EntreGuillemets(settings)
    eg.run()
    eg.report()
