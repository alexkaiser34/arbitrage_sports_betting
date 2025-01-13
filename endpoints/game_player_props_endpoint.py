from endpoints.base_endpoint import BaseEndpoint
from models.game_player_props_response import GamePlayerPropsResponse, Outcome, Market, Bookmaker
from typing import List
import json

class GamePlayerPropsEndpoint(BaseEndpoint):
    
    def __init__(self, baseUrl :str, apiKey :str, sport :str, eventId, regions :str, bookmakers :str, oddsFormat :str, dateFormat :str, markets: str):
        super().__init__(baseUrl, apiKey)
        self.result : str = ""        
        self.sport = sport

        self.eventId = eventId
        self.regions = regions
        self.bookmakers = bookmakers
        self.oddsFormat = oddsFormat
        self.dateFormat = dateFormat
        self.markets = markets

        self.setEndpointUrl('/sports/' + self.sport + '/events/' + self.eventId + '/odds/')
        self.initialize_parameters()
        
    def initialize_parameters(self):
        d = {}
        d['apiKey'] = self.apiKey
        d['regions'] = self.regions
        d['bookmakers'] = self.bookmakers
        d['oddsFormat'] = self.oddsFormat
        d['dateFormat'] = self.dateFormat
        d['markets'] = self.markets
        self.setParameters(d)
        
    def get(self):
        json_response = super().get()
        self._store_results(json_response)

    def _store_results(self, response):
        
        # its easier to store this is as a plain JSON string
        # we need this data to create and pandas dataframe
        # we can simply use this response to create the dataframe
        # by using pd.read_json()
        # We can view the game_player_props_response model to see the deconstructed
        # json in the form of classes
        
        self.result = response
        
    # not used
    def _json_to_object(self,response):
        bookmakers : List[Bookmaker] = []
        j = json.loads(response)
    
        for bm in j['bookmakers']:
            markets : List[Market] = []
            temp_bookmaker = Bookmaker(
                bm['key'],
                markets
            )
            for mrkt in bm['markets']:
                outcomes : List[Outcome] = []
                temp_market = Market(
                    mrkt['key'],
                    mrkt['last_update'],
                    outcomes
                    
                )
                for outc in mrkt['outcomes']:
                    if 'point' in outc:
                        temp_outcome = Outcome(
                            outc['name'],
                            outc['description'],
                            outc['price'],
                            outc['point']
                        )
                        outcomes.append(temp_outcome)
                markets.append(temp_market)
            bookmakers.append(temp_bookmaker)
            
        self.result = GamePlayerPropsResponse(
            j['id'],
            j['sport_key'],
            j['sport_title'],
            j['commence_time'],
            j['home_team'],
            j['away_team'],
            bookmakers
        )
            
    def print_results(self):
        for bookmaker in self.result.bookmakers:
            for market in bookmaker.markets:
                for outcome in market.outcomes:
                    print(outcome.description)