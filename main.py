from app import App
from dynamodb import DynamoDbConfig
    
def main():
    dynamo = DynamoDbConfig()
    appConfig = dynamo.getConfig()

    if appConfig.enabled:
        app = App(
            appConfig.sports,
            appConfig.wager,
            appConfig.bookmakers,
            appConfig.regions
        )
        app.run()
    else:
        print("App is currently disabled")

if __name__ == "__main__":
    main()