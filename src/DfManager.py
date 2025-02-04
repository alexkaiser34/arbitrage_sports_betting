import pandas as pd
import numpy as np
import json
import os
from io import StringIO
from ArbitrageAlgorithm import ArbitrageAlgorithm, WinningBet, SingleBet
from typing import List, Tuple, Dict

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

MLB_MARKET_MAP = {
    "batter_home_runs": [ "batter_home_runs_alternate" ],
    "batter_total_bases": [ "batter_total_bases_alternate" ],
    "batter_hits": [ "batter_hits_alternate" ],
    "batter_rbis": [ "batter_rbis_alternate" ],
    "pitcher_hits_allowed": [ "pitcher_hits_allowed_alternate" ],
    "pitcher_walks": [ "pitcher_walks_alternate" ],
    "pitcher_strikeouts": [ "pitcher_strikeouts_alternate" ]
}

MARKET_MAP = {
    "americanfootball_nfl": NFL_MARKET_MAP,
    "basketball_nba": NBA_MARKET_MAP,
    "baseball_mlb": MLB_MARKET_MAP,
    "basketball_ncaab": NBA_MARKET_MAP,
    "americanfootball_ncaaf": NFL_MARKET_MAP
}

class DfManager:
    
    def __init__(self, jsonString: str, sport: str):
        self.m_sport: str = sport
        self.m_initial_df: pd.DataFrame = self.create_df_from_json(jsonString)
        self.df: pd.DataFrame = None
        self.m_data: List[SingleBet] = self._populate_data()
        self.m_valid_bets: Dict[str, List[Tuple[SingleBet, List[SingleBet]]]] = {}
    
    def create_df_from_json(self, jsonString:str) -> pd.DataFrame:
        # converting json string into pandas dataframe
        try:
            j = '[' + jsonString + ']'
            return pd.read_json(StringIO(j))
        except Exception as e:
            print('Invalid JSON string')
            print(jsonString)
        return pd.DataFrame()
    
    def _populate_data(self) -> List[SingleBet]:
        """Optimized data population using list comprehensions."""
        return [
            SingleBet(
                row['id'], row['commence_time'], market['last_update'], bookmaker['key'], 
                market['key'], outcome['description'], 'O' if outcome['name'] == 'Over' else 'U', 
                outcome['price'], outcome['point']
            )
            for _, row in self.m_initial_df.iterrows()
            for bookmaker in row['bookmakers']
            for market in bookmaker['markets']
            for outcome in market['outcomes'] if "point" in outcome
        ]
                
    def create_valid_bets(self):
        """Find valid bets using optimized filtering."""
        self.df = pd.DataFrame.from_records([bet.to_dict() for bet in self.m_data])
        if not self.df.empty:
            for name in self.df['name'].unique():
                self.find_valid_bets(self.df[self.df['name'] == name])

    def find_valid_bets(self, df: pd.DataFrame):
        """Optimized filtering using NumPy operations."""
        uniqueBets = set(df['betType'].unique())
        commonBets = uniqueBets.intersection(set(MARKET_MAP[self.m_sport].keys()))
        
        for betType in commonBets:
            validBetTypes: List[str] = []
            validBetTypes.append(betType)
            validBetTypes.extend(MARKET_MAP[self.m_sport][betType])

            valid_bets = df.query("betType in @validBetTypes")
            
            over_bets = valid_bets[valid_bets['o/u'] == 'O']
            under_bets = valid_bets[valid_bets['o/u'] == 'U']
            
            for _, over in over_bets.iterrows():
                close_bets: pd.DataFrame = under_bets[np.abs(under_bets['point'] - over['point']) <= 0.6]
                
                # one bet needs to have positive odds...
                if over['price'] < 0:
                    close_bets = close_bets[close_bets['price'] > 0]

                if not close_bets.empty:
                    # create all of the valid bets
                    valid_close_bets = [
                        SingleBet(
                            bet['game_id'],
                            bet['commence_time'],
                            bet['last_update'],
                            bet['bookmaker'],
                            bet['betType'],
                            bet['name'],
                            bet['o/u'],
                            bet['price'],
                            bet['point'] 
                        ) for bet in close_bets.to_dict(orient='records')]

                    over_bet = SingleBet(
                        over['game_id'],
                        over['commence_time'],
                        over['last_update'],
                        over['bookmaker'],
                        over['betType'],
                        over['name'],
                        over['o/u'],
                        over['price'],
                        over['point']
                    )
                    
                    # append the array
                    self.m_valid_bets.setdefault(over['name'], []).append((over_bet, valid_close_bets))
    
    def parse_valid_bets(self) -> str:
        s = ""
        for player in self.m_valid_bets.keys():
            
            s += "=============================================\n"
            s += "Bet summary for " + player + "\n"
            
            for valid_bets in self.m_valid_bets[player]:
                s+= "+++++++++++++++++++++++++++++++++++\n"
                s+= f'MAIN BET\n\t -- {valid_bets[0]}\n'
                s+= 'VALID BETS\n'
                for v in valid_bets[1]:
                    s+= f'\t -- {v}\n'
        return s