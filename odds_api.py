
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List

class OddsAPI:
    API_KEY='a0e1d956578423ef5f949b3380de5e51'
    # REGIONS='us,us2'
    # REGIONS='us,us2,us_dfs'
    # BOOKMAKERS='draftkings,fanduel,williamhill_us,espnbet,betmgm,fliff'
    # REGIONS='us,us2'
    # REGIONS='us'
    # BOOKMAKERS='draftkings,fanduel'
    # BOOKMAKERS='draftkings,fanduel,williamhill_us,espnbet,betmgm,fliff,prizepicks,underdog'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    
    MARKET_FILE_DICT = {
        "americanfootball_nfl": 'configs/nfl_markets_player_props.txt', 
        "basketball_nba": 'configs/nba_markets_player_props.txt'
    }

    # pass in sport to look at
    # we can change the sport of the API instance by calling its change_sport method
    def __init__(self, sport, bookmakers, regions):
        self.m_apiKey = OddsAPI.API_KEY
        self.m_regions = regions
        self.m_oddsFormat = OddsAPI.ODDS_FORMAT
        self.m_dateFormat = OddsAPI.DATE_FORMAT
        self.m_baseUrl = OddsAPI.BASE_URL
        self.m_bookMakers = bookmakers
        
        self.upcomingGames : List[str] = []
        self.response_data : List[str] = []
        
        self.games: List[UpcomingEventsEndResponse] = []

        self.m_sport = ""
        self.m_marketFile = ""
        self.change_sport(sport)
        
    # update appropriate data when we change the sport
    def change_sport(self, sport):
        self.m_sport = sport
        self.m_marketFile = OddsAPI.MARKET_FILE_DICT[self.m_sport]
        self.getUpcomingGames()
        
    def getUpcomingGames(self):
        
        self.upcomingGames.clear()
        self.games.clear()
        
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
            self.games.append(item)
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