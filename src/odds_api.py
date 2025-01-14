
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List, Dict
import os

class OddsAPI:
    API_KEY='a0e1d956578423ef5f949b3380de5e51'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    
    MARKET_FILE_DICT = {
        "americanfootball_nfl": str(os.path.join(os.path.dirname(__file__), './configs/nfl_markets_player_props.txt')), 
        "basketball_nba": str(os.path.join(os.path.dirname(__file__), './configs/nba_markets_player_props.txt')),
        "baseball_mlb": str(os.path.join(os.path.dirname(__file__), '.configs/mlb_markets_player_props.txt'))
    }
    
    IGNORED_MARKETS_LIVE_DICT = {
        "americanfootball_nfl": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_nfl_markets_live.txt')), 
        "basketball_nba": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_nba_markets_live.txt')),
        "baseball_mlb": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_mlb_markets_live.txt'))
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
        
        self.markets: Dict[str, str] = {}
        
        self.upcomingGames : Dict[str, List[str]] = {}
        self.response_data : Dict[str, List[str]] = {}
        
        self.games: List[UpcomingEventsEndResponse] = []

        self.m_sport: List[str] = sport
        self.getUpcomingGames()
        self.setupMarkets()
        
    def setupMarkets(self):
        for sport in self.m_sport:
            self.markets[sport] = self.readSupportedMarkets(sport)
            live_sport_markets = sport + "_live"
            self.markets[live_sport_markets] = self.readLiveMarkets(sport)
            
            
    def readLiveMarkets(self, sport):
        s = ''
        valid = set(line.strip() for line in open(OddsAPI.MARKET_FILE_DICT[sport]))
        invalid_live = set(line.strip() for line in open(OddsAPI.IGNORED_MARKETS_LIVE_DICT[sport]))

        result_set = valid - invalid_live
        numberOfLines = len(result_set)
        
        for num, item in enumerate(result_set):
            if num == (numberOfLines-1):
                s += item
            else:
                s += item + ','
                    
        return s

    def readSupportedMarkets(self, sport):
        s = ''
        with open(OddsAPI.MARKET_FILE_DICT[sport], 'r') as fp:
            lines = fp.read().splitlines()
            numberOfLines = len(lines)
            for num, line in enumerate(lines):
                if num == (numberOfLines-1):
                    s += line
                else:
                    s += line + ','
        return s
            
        
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
                
                
    def find_game(self, id) -> UpcomingEventsEndResponse:
        for game in self.games:
            if game.id == id:
                return game
                
    def getPlayerProps(self):

        self.response_data.clear()
        
        for sport in self.m_sport:
            if sport not in self.response_data:
                self.response_data[sport] = []
                
            for gameId in self.upcomingGames[sport]:
                game = self.find_game(gameId)
                markets = ""
                if game.upcoming:
                    markets = self.markets[sport]
                else:
                    sport_string = sport + "_live"
                    markets = self.markets[sport_string]

                gamePlayerPropsEndpoint = GamePlayerPropsEndpoint(
                    self.m_baseUrl,
                    self.m_apiKey,
                    sport,
                    gameId,
                    self.m_regions,
                    self.m_bookMakers,
                    self.m_oddsFormat,
                    self.m_dateFormat,
                    markets
                )
                gamePlayerPropsEndpoint.get()
                self.response_data[sport].append(gamePlayerPropsEndpoint.result)