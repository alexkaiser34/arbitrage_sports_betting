import pandas as pd
from pandas import DataFrame
import json
from io import StringIO
from ArbitrageAlgorithm import ArbitrageAlgorithm, WinningBet, SingleBet
from typing import List, Tuple

##################### DF Schema ##################
# game_id   commence_time   last_update   bookmaker  betType  name  O/U  price  point

NFL_MARKET_MAP = {
    "player_field_goals": [ "player_field_goals_alternate" ],
    "player_kicking_points": [ "player_kicking_points_alternate" ],
    "player_pass_attempts": [ "player_pass_attempts_alternate" ],
    "player_pass_completions": [ "player_pass_completions_alternate" ],
    "player_pass_interceptions": [ "player_pass_interceptions_alternate" ],
    "player_pass_longest_completion": [ "player_pass_longest_completion_alternate" ],
    "player_pass_tds": [ "player_pass_tds_alternate" ],
    "player_pass_yds": [ "player_pass_yds_alternate" ],
    "player_receptions": [ "player_receptions_alternate" ],
    "player_receptions_longest": [ "player_receptions_longest_alternate" ],
    "player_reception_tds": [ "player_reception_tds_alternate" ],
    "player_reception_yds": [ "player_reception_yds_alternate" ],
    "player_rush_attempts": [ "player_rush_attempts_alternate" ],
    "player_rush_longest": [ "player_rush_longest_alternate" ],
    "player_rush_reception_tds": [ "player_rush_reception_tds_alternate" ],
    "player_rush_reception_yds": [ "player_rush_reception_yds_alternate" ],
    "player_rush_tds": [ "player_rush_tds_alternate" ],
    "player_rush_yds": [ "player_rush_yds_alternate" ]

}

NBA_MARKET_MAP = {
    "player_points": [ "player_points_alternate" ],
    "player_rebounds": [ "player_rebounds_alternate" ],
    "player_assists": [ "player_assists_alternate" ],
    "player_threes": [ "player_threes_alternate" ],
    "player_blocks": [ "player_blocks_alternate" ],
    "player_steals": [ "player_steals_alternate" ],
    "player_points_rebounds_assists": [ "player_points_rebounds_assists_alternate" ],
    "player_points_rebounds": [ "player_points_rebounds_alternate" ],
    "player_points_assists": [ "player_points_assists_alternate" ],
    "player_rebounds_assists": [ "player_rebounds_assists_alternate" ]
}

class DfManager:
    
    def __init__(self, jsonString: str, sport: str):
        self.m_jsonString: str = jsonString
        self.m_sport: str = sport
        
        self.m_initial_df: DataFrame = self.create_df_from_json(self.m_jsonString)
        self.df: DataFrame = None
        
        self.m_data: List[SingleBet] = []
        self.m_valid_bets: dict[str, List[Tuple[SingleBet, List[SingleBet]]]] = {}
        self.m_betTypes: set[str] = set()
        self.m_playerNames: set[str] = set()
        self.m_bookmakers: set[str] = set()

        self.populate_data()
    
    def create_df_from_json(self, jsonString) -> DataFrame:
        # converting json string into pandas dataframe
        df = pd.read_json(StringIO(jsonString))
        return df
    
    def populate_data(self):
        for index, row in self.m_initial_df.iterrows():
            bets = []        
            gameId = row['id']
            commence_time = row['commence_time']
            bets = self._create_bets(row['bookmakers'], gameId, commence_time)
            self.m_data.extend(bets)
            
        self.df = pd.DataFrame.from_records([data.to_dict() for data in self.m_data])
    
    def _create_bets(self, bookmaker, gameId, commence_time):
        bets = []
        bookMakerName = bookmaker['key']
        self.m_bookmakers.add(bookMakerName)
        for market in bookmaker['markets']:
            bet_type = market['key']
            self.m_betTypes.add(bet_type)
            last_update = market['last_update']
            for outcome in market['outcomes']:
                # ignore data with no point...
                if "point" in outcome:
                    name = outcome['description']
                    o_u = ''
                    if outcome['name'] == 'Over':
                        o_u = 'O'
                    else:
                        o_u = 'U'
                    price = outcome['price']
                    point = outcome['point']
                    bet = SingleBet(gameId, commence_time, last_update, bookMakerName, bet_type, name, o_u, price, point)
                    bets.append(bet)
                    self.m_playerNames.add(name)
        return bets
                
                
    def create_valid_bets(self):
        # go through each player name and find valid bets...
        for name in self.m_playerNames:
            filtered_df: DataFrame= self.df[self.df['name'] == name]
            self.find_valid_bets(filtered_df)
            
    def find_valid_bets(self, df: DataFrame):
        for betType in self.m_betTypes:
            validBetTypes: List[str] = []
            validBetTypes.append(betType)

            if self.m_sport == "basketball_nba":
                if betType in NBA_MARKET_MAP.keys():
                    validBetTypes.extend(NBA_MARKET_MAP[betType])
            elif self.m_sport == "americanfootball_nfl":
                if betType in NFL_MARKET_MAP.keys():
                    validBetTypes.extend(NFL_MARKET_MAP[betType])
                
            bt_filter: DataFrame = df[df['betType'].isin(validBetTypes)]
            if not bt_filter.empty:
                o_filter: DataFrame = bt_filter[bt_filter['o/u'] == 'O']
                u_filter: DataFrame = bt_filter[bt_filter['o/u'] == 'U']
            
                for indexO, overRow in o_filter.iterrows():
                    temp = []
                    found = False
                    valid = False
                    if (overRow['price'] > 0):
                        valid = True
                    
                    for indexU, underRow in u_filter.iterrows():
                        if abs(underRow['point'] - overRow['point']) <= 0.6:
                            if (((not valid) and (underRow['price'] > 0)) or valid):
                                found = True
                                under_bet = SingleBet(
                                    underRow['game_id'],
                                    underRow['commence_time'],
                                    underRow['last_update'],
                                    underRow['bookmaker'],
                                    underRow['betType'],
                                    underRow['name'],
                                    underRow['o/u'],
                                    underRow['price'],
                                    underRow['point']
                                )
                                temp.append(under_bet)
                    if found and valid:
                        over_bet = SingleBet(
                                overRow['game_id'],
                                overRow['commence_time'],
                                overRow['last_update'],
                                overRow['bookmaker'],
                                overRow['betType'],
                                overRow['name'],
                                overRow['o/u'],
                                overRow['price'],
                                overRow['point']
                            )
                        if over_bet.name not in self.m_valid_bets:
                            self.m_valid_bets[over_bet.name] = []
                        self.m_valid_bets[over_bet.name].append((over_bet, temp))
    
    def parse_valid_bets(self):
        for player in self.valid_bets.keys():
            print("=============================================")
            print("Bet summary for " + player + "\n")
            
            for valid_bets in self.valid_bets[player]:
                print("+++++++++++++++++++++++++++++++++++")
                print(f'MAIN BET\n\t -- {valid_bets[0]}\n')
                print('VALID BETS')
                for v in valid_bets[1]:
                    print(f'\t -- {v}')