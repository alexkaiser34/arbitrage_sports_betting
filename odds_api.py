
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List, Dict

class OddsAPI:
    API_KEY='a0e1d956578423ef5f949b3380de5e51'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    
    MARKET_FILE_DICT = {
        "americanfootball_nfl": 'configs/nfl_markets_player_props.txt', 
        "basketball_nba": 'configs/nba_markets_player_props.txt',
        "baseball_mlb": 'configs/mlb_markets_player_props.txt'
    }

    # pass in sport to look at
    # we can change the sport of the API instance by calling its change_sport method
    def __init__(self, sport: List[str], bookmakers: str, regions: str):
        self.m_apiKey = OddsAPI.API_KEY
        self.m_regions = regions
        self.m_oddsFormat = OddsAPI.ODDS_FORMAT
        self.m_dateFormat = OddsAPI.DATE_FORMAT
        self.m_baseUrl = OddsAPI.BASE_URL
        self.m_bookMakers = bookmakers
        
        self.upcomingGames : Dict[str, List[str]] = {}
        self.response_data : Dict[str, List[str]] = {}
        
        self.games: List[UpcomingEventsEndResponse] = []

        self.m_sport: List[str] = sport
        self.getUpcomingGames()
        
    def getUpcomingGames(self):
        
        self.upcomingGames.clear()
        self.games.clear()
        
        for sport in self.m_sport:
            if sport not in self.upcomingGames:
                self.upcomingGames[sport] = []
                
             # set up endpoint
            upcomingEventsEndpoint = UpcomingEventsEndpoint(
                self.m_baseUrl,
                self.m_apiKey,
                sport
            )
            
            # populate result
            upcomingEventsEndpoint.get()
            
            # store gameIds 
            for item in upcomingEventsEndpoint.result:
                self.games.append(item)
                self.upcomingGames[sport].append(item.id)
                
    def getPlayerProps(self):

        self.response_data.clear()
        
        for sport in self.m_sport:
            marketFile = OddsAPI.MARKET_FILE_DICT[sport]        
            if sport not in self.response_data:
                self.response_data[sport] = []
                
            for gameId in self.upcomingGames[sport]:
                gamePlayerPropsEndpoint = GamePlayerPropsEndpoint(
                    self.m_baseUrl,
                    self.m_apiKey,
                    sport,
                    gameId,
                    self.m_regions,
                    self.m_bookMakers,
                    self.m_oddsFormat,
                    self.m_dateFormat,
                    marketFile
                )
                gamePlayerPropsEndpoint.get()
                self.response_data[sport].append(gamePlayerPropsEndpoint.result)