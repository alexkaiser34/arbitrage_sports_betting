
from endpoints.available_sports_endpoint import AvailableSportsEndpoint
from endpoints.upcoming_events_endpoint import UpcomingEventsEndpoint
from endpoints.game_player_props_endpoint import GamePlayerPropsEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List, Dict, Tuple
import os
import json
from datetime import datetime, timezone
from dateutil import parser, tz
import concurrent.futures
import time


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
        "baseball_mlb": str(os.path.join(os.path.dirname(__file__), './configs/mlb_markets_player_props.txt')),
        "basketball_ncaab": str(os.path.join(os.path.dirname(__file__), './configs/ncaab_markets_player_props.txt')),
        "americanfootball_ncaaf": str(os.path.join(os.path.dirname(__file__), './configs/ncaaf_markets_player_props.txt'))
    }

    IGNORED_MARKETS_LIVE_DICT = {
        "americanfootball_nfl": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_nfl_markets_live.txt')), 
        "basketball_nba": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_nba_markets_live.txt')),
        "baseball_mlb": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_mlb_markets_live.txt')),
        "basketball_ncaab": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_ncaab_markets_live.txt')),
        "americanfootball_ncaaf": str(os.path.join(os.path.dirname(__file__),'./configs/ignored_ncaaf_markets_live.txt'))   
    }
    
    CACHE_FILE = '/tmp/upcoming_events_cache.json'

    # set to True to use cache
    # we will use false now because we need to be able to detect
    # when a game finishes...
    USE_CACHE = False

    # we do not want to look at more than this amount of games
    MAX_GAMES = 30

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

        if OddsAPI.USE_CACHE:
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

        cached_time = parser.parse(self.cache[sport].timestamp).astimezone(OddsAPI.TIME_ZONE)
        now = datetime.now(timezone.utc).astimezone(OddsAPI.TIME_ZONE)

        if cached_time.hour == 8 and now.hour >= 15:
            self.remove_cache()
            return False
        else:
            # 3 PM - 8 AM is 17 hours...
            if ((now.timestamp() - cached_time.timestamp()) > (17*60*60)):
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
            
    def fetchUpcomingGames(self, sport) -> Tuple[str, List[str], List[UpcomingEventsEndResponse]]:
        if OddsAPI.USE_CACHE:
            if self._isCacheValid(sport):
                temp_games = []

                # update upcoming status
                self._updateIsGameUpcoming(self.cache[sport].data)

                # store all games
                if self.liveEnabled:
                    temp_games = self.cache[sport].data
                else:
                    temp_games = [game for game in self.cache[sport].data if game.upcoming]

                return sport, [game.id for game in temp_games], temp_games
        
        # make API request if cache is not valid
        game_ids = []
        games = []
        
        upcomingEventsEndpoint = UpcomingEventsEndpoint(
                    self.m_baseUrl,
                    self.m_apiKey,
                    sport
                )

        # populate result
        if (upcomingEventsEndpoint.get()):
            # store games and IDs
            for item in upcomingEventsEndpoint.result:
                if self.liveEnabled or item.upcoming:
                    games.append(item)
                    game_ids.append(item.id)

            if OddsAPI.USE_CACHE:
                # set the cache
                # if we execute this between midnight and 8 AM, set the timestamp to 8 AM
                # if we execute this after 8 AM, set the timestamp to 3 PM
                # we should always be executing this at 8 AM and 3 PM
                # according to logic in self._isCacheValid
                now = datetime.now().astimezone(OddsAPI.TIME_ZONE)
                if now.hour <= 8:
                    now = now.replace(hour=8, minute=0, second=0, microsecond=0)
                else:
                    now = now.replace(hour=15, minute=0, second=0, microsecond=0)

                    self.cache[sport] = CacheFormat(now.isoformat(), upcomingEventsEndpoint.result)
                    self.save_cache()

        return sport, game_ids, games

    def _balanceGames(self):
        num_games = len(self.games)
        max_games = OddsAPI.MAX_GAMES
        
        # balance games when we have more than MAX_GAMES
        if num_games > max_games:
            max_games_per_sport = max_games // len(self.upcomingGames)

            # Create a new dictionary to hold the balanced games
            balanced_upcoming_games = {}
            balanced_games = []

            # First, add up to max_games_per_sport games for each sport
            for sport, game_ids in self.upcomingGames.items():
                balanced_upcoming_games[sport] = game_ids[:max_games_per_sport]
                balanced_games.extend(game_ids[:max_games_per_sport])

            remaining_games = max_games - len(balanced_games)
            sport_indices = {sport: max_games_per_sport for sport in self.upcomingGames}

            while remaining_games > 0:
                for sport, game_ids in self.upcomingGames.items():
                    if remaining_games <= 0:
                        break
                    current_index = sport_indices[sport]
                    if current_index < len(game_ids):
                        balanced_upcoming_games[sport].append(game_ids[current_index])
                        balanced_games.append(game_ids[current_index])
                        sport_indices[sport] += 1
                        remaining_games -= 1

            # Update self.upcomingGames and self.games
            self.upcomingGames = balanced_upcoming_games
            self.games = [game for game in self.games if game.id in balanced_games]

    def _printGames(self):
        print('--------- GAME INFO ----------- ')
        print(f'\nTotal number of games = {len(self.games)}\n')
        for sport in self.upcomingGames:
            print(f'\n{sport} has {len(self.upcomingGames[sport])} games\n')
            print(self.upcomingGames[sport])
        print('------------------------------- ')

    def getUpcomingGames(self):
        self.upcomingGames.clear()
        self.games.clear()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetchUpcomingGames, sport) for sport in self.m_sport]
            for future in concurrent.futures.as_completed(futures):
                sport, game_ids, games = future.result()
                self.upcomingGames[sport] = game_ids
                self.games.extend(games)

        self._balanceGames()
        self._printGames()
                
    def find_game(self, id) -> UpcomingEventsEndResponse:
        for game in self.games:
            if game.id == id:
                return game
            
    def fetchPlayerPropsForGame(self, gameId, sport, delay: float, count: int) -> Tuple[str, str]:
        '''Fetch player props for a given game'''
        # small delay to avoid exceeding rate limit
        if delay > 0.0001:
            time.sleep(delay * count)

        game = self.find_game(gameId)
        if game:
            markets = self.markets[sport] if game.upcoming else self.markets[sport + "_live"]
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
            if (gamePlayerPropsEndpoint.get()):
                return gamePlayerPropsEndpoint.result, sport
        return "", sport
        
    def fetchPlayerProps(self, sport, delay: float, count: int):
        # small delay in between sports
        if delay > 0.0001:
            time.sleep(delay * count)
        num_games = len(self.games)
        delay = 0

        # add in logic to increase delay with large number of games
        # without this, we will exceed the rate limit
        if num_games > (len(self.m_sport) * 20):
            delay = 1.0 / 20.0

        # start a thread for each game
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetchPlayerPropsForGame, gameId, sport, delay, count) for count, gameId in enumerate(self.upcomingGames[sport])]
            for future in concurrent.futures.as_completed(futures):
                data, sport = future.result()
                if data != "":
                    if sport not in self.response_data:
                        self.response_data[sport] = []
                    self.response_data[sport].append(data)
                        
    def getPlayerProps(self):

        self.response_data.clear()
        
        # create a small delay in sports
        delay = 1 if len(self.m_sport) > 1 else 0

        # start a thread for each sport
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetchPlayerProps, sport, delay, count) for count, sport in enumerate(self.m_sport)]
            for future in concurrent.futures.as_completed(futures):
                future.result()