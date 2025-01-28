from app import App
from dynamodb import DynamoDbConfig, Config
import os
import json


# set this to true when grabbing application config from DynamoDB
# otherwise, we will use a local file
# NOTE: Using a local file in a lambda function is not recommended
# as the file system is ephemeral
USE_DYNAMODB = True

# helper classes to parse local JSON file config
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
    try:
        if appConfig is not None:
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
        else:
            print("Error loading config")
    except Exception as e:
        print(f"Error running app: {str(e)}")

def handler(event, context):

    # use a local file to store application config
    # this is not recommended in a lambda function
    if not USE_DYNAMODB:
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
    else:
        dynamo = DynamoDbConfig()
        appConfig = dynamo.getConfig()
        lets_begin(appConfig)