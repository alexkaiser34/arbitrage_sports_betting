
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List, Dict
import os
import json
from datetime import datetime, timezone
from dateutil import parser, tz


class CacheFormat:
    def __init__(self, timestamp, data: List[UpcomingEventsEndResponse]):
        self.timestamp: str = timestamp
        self.data: List[UpcomingEventsEndResponse] = data

    def toDict(self):
        return {
            "timestamp": self.timestamp,
            "data": self.data
        }

class CacheEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CacheFormat):
            return obj.toDict()
        elif isinstance(obj, UpcomingEventsEndResponse):
            return obj.toDict()
        return json.JSONEncoder.default(self, obj)

class CacheDecoder(json.JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        obj = super().decode(s, _w)
        res: Dict[str, CacheFormat] = {}

        # Custom logic: Construct the cache object
        for sport in obj.keys():
            tmpList : List[UpcomingEventsEndResponse] = []
            for item in obj[sport]['data']:
                tmpList.append(
                    UpcomingEventsEndResponse(
                        item['id'],
                        item['sports_key'],
                        item['sport_title'],
                        item['commence_time'],
                        item['home_team'],
                        item['away_team']
                    )
                )

            res[sport] = CacheFormat(obj[sport]['timestamp'], tmpList)

        return res

class OddsAPI:
    API_KEY='a0e1d956578423ef5f949b3380de5e51'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    TIME_ZONE = tz.gettz('America/New_York')
    
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
    
    CACHE_FILE = str(os.path.join(os.path.dirname(__file__), './upcoming_events_cache.json'))

    # pass in sport to look at
    # we can change the sport of the API instance by calling its change_sport method
    def __init__(self, live_enabled: bool, sport: List[str], bookmakers: str, regions: str):
        self.liveEnabled = live_enabled
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

        # cache games, we want to make this API call whenever a new sport is added
        # or a new day occurs
        self.cache: Dict[str, CacheFormat] = {}
        self.load_cache()

        self.m_sport: List[str] = sport
        self.getUpcomingGames()
        self.setupMarkets()
        
    def load_cache(self):
        if os.path.exists(OddsAPI.CACHE_FILE):
            with open(OddsAPI.CACHE_FILE, 'r') as cache_file:
                cache_data = json.load(cache_file, cls=CacheDecoder)
                self.cache = cache_data

    def save_cache(self):
        with open(OddsAPI.CACHE_FILE, 'w') as cache_file:
            json.dump(self.cache, cache_file, indent=4, cls=CacheEncoder)

    def remove_cache(self):
        open(OddsAPI.CACHE_FILE, 'w').close()
        self.cache.clear()
        
    def _isCacheValid(self, sport):
        if not os.path.exists(OddsAPI.CACHE_FILE):
            return False

        if os.path.getsize(OddsAPI.CACHE_FILE) == 0:
            return False

        if len(self.cache) == 0:
            return False

        if sport not in self.cache.keys():
            return False

        cached_time = parser.parse(self.cache[sport].timestamp).astimezone(OddsAPI.TIME_ZONE).timestamp()
        now = datetime.now(timezone.utc).astimezone(OddsAPI.TIME_ZONE).timestamp()

        # update our games once a day... happens at 8 AM
        if (now - cached_time) > 86400:
            self.remove_cache()
            return False

        return True

    def setupMarkets(self):
        for sport in self.m_sport:
            self.markets[sport] = self.readSupportedMarkets(sport)
            live_sport_markets = sport + "_live"
            self.markets[live_sport_markets] = self.readLiveMarkets(sport)
       
    def readLiveMarkets(self, sport):
        valid = set(line.strip() for line in open(OddsAPI.MARKET_FILE_DICT[sport]))
        invalid_live = set(line.strip() for line in open(OddsAPI.IGNORED_MARKETS_LIVE_DICT[sport]))
        result_set = valid - invalid_live
        return ','.join(result_set)

    def readSupportedMarkets(self, sport):
        with open(OddsAPI.MARKET_FILE_DICT[sport], 'r') as fp:
            lines = fp.read().splitlines()
        return ','.join(lines)
    
    def _updateIsGameUpcoming(self, games: List[UpcomingEventsEndResponse]):
        for game in games:
            game.updateUpcoming()
    
    def getUpcomingGames(self):
        
        self.upcomingGames.clear()
        self.games.clear()
        
        for sport in self.m_sport:
            if sport not in self.upcomingGames:
                self.upcomingGames[sport] = []
                
            if self._isCacheValid(sport):
                temp_games = []
                
                # update upcoming status
                self._updateIsGameUpcoming(self.cache[sport].data)

                # store all games
                if self.liveEnabled:
                    temp_games = self.cache[sport].data
                else:
                    temp_games = [game for game in self.cache[sport].data if game.upcoming]

                self.games.extend(temp_games)
                self.upcomingGames[sport] = [game.id for game in temp_games]
            else:
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
                    if self.liveEnabled:
                        self.games.append(item)
                        self.upcomingGames[sport].append(item.id)
                    else:
                        # upcoming games only
                        if item.upcoming:
                            self.games.append(item)
                            self.upcomingGames[sport].append(item.id)

                eight_AM_today = datetime.now().astimezone(OddsAPI.TIME_ZONE).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()
                self.cache[sport] = CacheFormat(eight_AM_today, upcomingEventsEndpoint.result)
                self.save_cache()
                
                
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
                if game:
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