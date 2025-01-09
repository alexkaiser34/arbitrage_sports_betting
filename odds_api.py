
from endpoint import EndPoint

class OddsAPI:
    API_KEY='414053fc79db1a33165e95d3ec2c89ce'
    REGIONS='us'
    ODDS_FORMAT='american'
    DATE_FORMAT='iso'
    BASE_URL = 'https://api.the-odds-api.com/v4'
    NBA_MARKETS = 'configs/nba_markets_player_props.txt'
    NFL_MARKETS = 'configs/nfl_markets_player_props.txt'
    SUPPORTED_SPORTS = 'configs/supported_sports.txt'
    
    # pass in sport to look at
    def __init__(self, sport):
        self.m_apiKey = OddsAPI.API_KEY
        self.m_regions = OddsAPI.REGIONS
        self.m_dateFormat = OddsAPI.DATE_FORMAT
        self.m_baseUrl = OddsAPI.BASE_URL
        
        self.m_sport = sport
        
        self.m_nbaMarkets = ''
        self.m_nflMarkets = ''
        self.m_upcomingEvents = []
        
        self.m_upcomingEventsEndpoint = None
        self.m_nbaPlayerPropsEndpoint = None
        self.m_nflPlayerPropsEndpoint = None
        
        self.read_configs()
        self.setupEndpoints()
        
    def set_sport(self, sport):
        self.m_sport = sport

    def read_configs(self):
        self.m_nbaMarkets = self._read_file(OddsAPI.NBA_MARKETS)
        self.m_nflMarkets = self._read_file(OddsAPI.NFL_MARKETS)
        
    def _read_file(self, file_path):
        s = ''
        with open(file_path, 'r') as fp:
            lines = fp.read().splitlines()
            numberOfLines = len(lines)
            for num, line in enumerate(lines):
                if num == (numberOfLines-1):
                    s += line
                else:
                    s += line + ','
                    
        return s
    
    def getUpcomingGames(self):
        res = self.m_upcomingEventsEndpoint.get()
        print(res)
        
    def setupEndpoints(self):
        
        # available sports endpoint
        self.m_upcomingEventsEndpoint = EndPoint(self.m_baseUrl)
        self.m_upcomingEventsEndpoint.setEndpointUrl('/sports/' + self.m_sport + '/events')
        self.m_upcomingEventsEndpoint.setParameters({'api_key': self.API_KEY})
        
        self.m_nbaPlayerPropsEndpoint = EndPoint(self.m_baseUrl)
        self.m_nflPlayerPropsEndpoint = EndPoint(self.m_baseUrl)
#         self.m_nbaPlayerPropsEndpoint.setEndpointUrl('/sports/basketball_nbas')
#         self.m_nbaPlayerPropsEndpoint.setParameters({'api_key': self.API_KEY})
#         sport = "basketball_nba"
# eventId= "e49c35167662c7e6ea6970b981b018f8"
# markets = 'player_points,player_points_q1,player_rebounds,player_rebounds_q1,player_assists,player_assists_q1,player_threes,player_blocks,player_steals,player_blocks_steals,player_turnovers,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists,player_field_goals,player_frees_made,player_frees_attempts,player_first_basket,player_double_double,player_triple_double,player_method_of_first_basket,player_points_alternate,player_rebounds_alternate,player_assists_alternate,player_blocks_alternate,player_steals_alternate,player_threes_alternate,player_points_assists_alternate,player_points_rebounds_alternate,player_rebounds_assists_alternate,player_points_rebounds_assists_alternate'

#         odds_response= requests.get(
#     'https://api.the-odds-api.com/v4/sports/' + sport + '/events/'  + eventId + '/odds',
#     params={
#         'api_key': API_KEY,
#         'regions': REGIONS,
#         'markets': markets,
#         'oddsFormat': ODDS_FORMAT
#     }
# )
        
        #     'https://api.the-odds-api.com/v4/sports', 
            #     params={
            #         'api_key': API_KEY
            #     }
        