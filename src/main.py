from app import App
import os
import json

class Config:
    def __init__(self, enabled: bool, live_enabled: bool, sports: str, regions: str, bookmakers: str, wager: str):
        self.enabled: bool = enabled
        self.live_enabled: bool = live_enabled
        self.sports: str = sports
        self.regions: str = regions
        self.bookmakers: str = bookmakers
        self.wager: int = int(wager)

    def __str__(self):
        return f'enabled={self.enabled},live_enabled={self.live_enabled}sports={self.sports},regions={self.regions},bookmakers={self.bookmakers},wager={str(self.wager)}'
    
    def toDict(self):
        return {
            "enabled": self.enabled,
            "live_enabled": self.live_enabled,
            "sports": self.sports,
            "regions": self.regions,
            "bookmakers": self.bookmakers,
            "wager": self.wager
        }

class ConfigEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Config):
            return obj.toDict()
        return json.JSONEncoder.default(self, obj)

class ConfigDecoder(json.JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        obj = super().decode(s, _w)
        return Config(
            obj['enabled'],
            obj['live_enabled'],
            obj['sports'],
            obj['regions'],
            obj['bookmakers'],
            obj['wager']
        )

def lets_begin(appConfig: Config):
    if appConfig.enabled:
        app = App(
            appConfig.live_enabled,
            appConfig.sports,
            appConfig.wager,
            appConfig.bookmakers,
            appConfig.regions
        )
        app.run()
    else:
        print("App is currently disabled")

def handler(event, context):

    file_path = '/tmp/application_config.json'

    if event and 'update' in event:
        try:
            # parse config from event
            config = Config(
                event['update']['enabled'],
                event['update']['live_enabled'], 
                event['update']['sports'],
                event['update']['regions'], 
                event['update']['bookmakers'],
                event['update']['wager']
            )

            print("Updating config")
            print(config)

            # write config to file
            with open(file_path, 'w') as config_file:
                json.dump(config, config_file, indent=4, cls=ConfigEncoder)

        except Exception as e:
            print(f"Error updating config: {str(e)}")
            return
    else:
        # regular operation
        if not os.path.exists(file_path):
            print("Application is not configured!!")
            print('Please use admin panel to configure the application')
            return

        config = None
        with open(file_path, 'r') as config_file:
            config = json.load(config_file, cls=ConfigDecoder)

        if config is None:
            print("Error loading config")
            return

        print("configured: Config is ")
        print(config)

        lets_begin(config)