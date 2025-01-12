import boto3

class Config:
    TABLE_NAME = "arbitrage-configuration"
    
    def __init__(self, enabled: bool, sports: str, regions: str, bookmakers: str, wager: str):
        self.enabled: bool = enabled
        self.sports: str = sports
        self.regions: str = regions
        self.bookmakers: str = bookmakers
        self.wager: int = int(wager)
        
    def __str__(self):
        return f'enabled={self.enabled},sports={self.sports},regions={self.regions},bookmakers={self.bookmakers},wager={str(self.wager)}'

class DynamoDbConfig:
    
    def __init__(self):
        self.config : Config = None
        self.dynamo_table = boto3.resource('dynamodb').Table(Config.TABLE_NAME)

    def getConfig(self) -> Config:
        response = self.dynamo_table.get_item(Key={'id': 1})
        item = response['Item']
        self.config = Config(
            item['enabled'],
            item['sports'],
            item['regions'],
            item['bookmakers'],
            item['wager']
        )
        
        return self.config