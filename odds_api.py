
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from typing import List
from io import StringIO

import pandas as pd

class OddsAPI:
    API_KEY='414053fc79db1a33165e95d3ec2c89ce'
    REGIONS='us,us2'
    BOOKMAKERS='draftkings,fanduel,espnbet,betmgm,fliff'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    NBA_MARKETS = 'configs/nba_markets_player_props.txt'
    NFL_MARKETS = 'configs/nfl_markets_player_props.txt'
    SUPPORTED_SPORTS=["americanfootball_nfl", "basketball_nba"]
    FOOTBALL = 0
    BASKETBALL = 1

    # pass in sport to look at
    # we can change the sport of the API instance by calling its change_sport method
    def __init__(self, sport):
        self.m_apiKey = OddsAPI.API_KEY
        self.m_regions = OddsAPI.REGIONS
        self.m_oddsFormat = OddsAPI.ODDS_FORMAT
        self.m_dateFormat = OddsAPI.DATE_FORMAT
        self.m_baseUrl = OddsAPI.BASE_URL
        self.m_bookMakers = OddsAPI.BOOKMAKERS
        
        self.upcomingGames : List[str] = []
        self.response_data : List[str] = []

        self.m_sport = ""
        self.m_marketFile = ""
        self.change_sport(sport)
        
    # update appropriate data when we change the sport
    def change_sport(self, sport):
        if sport not in OddsAPI.SUPPORTED_SPORTS:
            raise("Invalid sport for odds API: " + sport)        
        self.m_sport = sport
        
        if self.m_sport == OddsAPI.SUPPORTED_SPORTS[OddsAPI.FOOTBALL]:
            self.m_marketFile = OddsAPI.NFL_MARKETS
        else:
            self.m_marketFile = OddsAPI.NBA_MARKETS
        
        self.getUpcomingGames()
        
        
    def getUpcomingGames(self):
        
        self.upcomingGames.clear()
        
        # set up endpoint
        upcomingEventsEndpoint = UpcomingEventsEndpoint(
            self.m_baseUrl,
            self.m_apiKey,
            self.m_sport
        )
        
        # populate result
        upcomingEventsEndpoint.get()
        
        # store gameIds 
        # TODO: look at commence time or add api params to only retrieve a timeframe of data
        for item in upcomingEventsEndpoint.result:
            self.upcomingGames.append(item.id) 
    
    def getPlayerProps(self):

        self.response_data.clear()
        
        # we have to make a request for each game, can not do all at once...
        for gameId in self.upcomingGames:
            gamePlayerPropsEndpoint = GamePlayerPropsEndpoint(
                self.m_baseUrl,
                self.m_apiKey,
                self.m_sport,
                gameId,
                self.m_regions,
                self.m_bookMakers,
                self.m_oddsFormat,
                self.m_dateFormat,
                self.m_marketFile
            )
            gamePlayerPropsEndpoint.get()
            
            self.response_data.append(gamePlayerPropsEndpoint.result)
            break
            
    def create_df(self):
        
        for gamePlayerProps in self.response_data:
            df = pd.read_json(StringIO(gamePlayerProps))
            print(df)
            # df.to_csv("test_results.csv")
                   
            

def main():
    # odds_api = OddsAPI(OddsAPI.SUPPORTED_SPORTS[OddsAPI.BASKETBALL])
    # odds_api.getPlayerProps()
    # odds_api.create_df()
    
if __name__ == "__main__":
    main()
        