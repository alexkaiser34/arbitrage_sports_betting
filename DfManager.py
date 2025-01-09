import pandas as pd
import json
from ArbitrageAlgorithm import ArbitrageAlgorithm, WinningBet, SingleBet

## TO DO: We currently filter the dataframe by bet type...
## However, we want to ensure we look at alternate lines as well in some cases
## Alternate lines will have a different bet type
## We should create some type of map to ensure we compare standard and alternate lines when desired
## May just need to define which markets are considered alternates... we should always be including alternate
## markets with a standard market

##################### DF Schema ##################
# game_id   commence_time   bookmaker  betType  name  O/U  price  point

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

VALID_BOOKMAKERS = [
    "betmgm",
    "fanduel",
    "draftkings",
    "espnbet",
    "williamhill_us",
    "prizepicks",
    "underdog"
]

VALID_REGIONS = [
    "us",
    "us2",
    "us_dfs"
]

VALID_SPORTS = [
    "americanfootball_nfl",
    "basketball_nba"
]

FOOTBALL = 0
BASKETBALL = 1




class DfManager:
    
    def __init__(self, fileName, sport):
        self.fileName = fileName
        self.initial_df = self.create_df_from_json_file(self.fileName)
        self.df = None
        self.data = []
        self.valid_bets = {}
        self.betTypes = set()
        self.playerNames = set()
        self.bookmakers = set()
        self.sport = sport
        self.populate_data()
    
    def create_df_from_json_file(self, fileName):
        d = None
        # converting json dataset from dictionary to dataframe
        df = pd.read_json(fileName)
        return df
    
    def populate_data(self):
        for index, row in self.initial_df.iterrows():
            bets = []        
            gameId = row['id']
            commence_time = row['commence_time']
            bets = self._create_bets(row['bookmakers'], gameId, commence_time)
            self.data.extend(bets)
            
        self.df = pd.DataFrame.from_records([data.to_dict() for data in self.data])
            
    
    def _create_bets(self, bookmaker, gameId, commence_time):
        bets = []
        bookMakerName = bookmaker['key']
        if bookMakerName in VALID_BOOKMAKERS:
            self.bookmakers.add(bookMakerName)
            for market in bookmaker['markets']:
                bet_type = market['key']
                self.betTypes.add(bet_type)
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
                        bet = SingleBet(gameId, commence_time, bookMakerName, bet_type, name, o_u, price, point)
                        bets.append(bet)
                        self.playerNames.add(name)
        return bets
                
                
    def create_valid_bets(self):
        # go through each player name and find valid bets...
        for name in self.playerNames:
            filtered_df = self.df[self.df['name'] == name]
            self.find_valid_bets(filtered_df)
            
    def find_valid_bets(self, df):
        for betType in self.betTypes:
            validBetTypes = []
            validBetTypes.append(betType)

            if self.sport == VALID_SPORTS[BASKETBALL]:
                if betType in NBA_MARKET_MAP.keys():
                    validBetTypes.extend(NBA_MARKET_MAP[betType])
            elif self.sport == VALID_SPORTS[FOOTBALL]:
                if betType in NFL_MARKET_MAP.keys():
                    validBetTypes.extend(NFL_MARKET_MAP[betType])
                
            bt_filter = df[df['betType'].isin(validBetTypes)]
            if not bt_filter.empty:
                o_filter = bt_filter[bt_filter['o/u'] == 'O']
                u_filter = bt_filter[bt_filter['o/u'] == 'U']
            
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
                                overRow['bookmaker'],
                                overRow['betType'],
                                overRow['name'],
                                overRow['o/u'],
                                overRow['price'],
                                overRow['point']
                            )
                        if over_bet.name not in self.valid_bets:
                            self.valid_bets[over_bet.name] = []
                        self.valid_bets[over_bet.name].append((over_bet, temp))
    
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
        

def main():
    dfManageBasketball = DfManager('examples/wizards_vs_sixers.json', VALID_SPORTS[BASKETBALL])
    dfManagerFootball = DfManager('examples/chargers_game.json', VALID_SPORTS[FOOTBALL])
    dfManageBasketball.create_valid_bets() 
    dfManagerFootball.create_valid_bets()
    algo = ArbitrageAlgorithm(500)
    algo.find_profit(dfManageBasketball.valid_bets)
    print('------------ BASKETBALL DATA --------------')
    algo.print_winnings()
    algo.find_profit(dfManagerFootball.valid_bets)
    print('------------ FOOTBALL DATA --------------')
    algo.print_winnings()
    
    # if algo.max_amount > 0:
    #     print("We have found a profit....")
    #     print("--------------- BET 1 ---------------")
    #     print(algo.bet1)
    #     print("--------------- BET 2 ---------------")
    #     print(algo.bet2)
    #     print("--------------- TOTAL WINNINGS ---------------")
    #     print(str(algo.total_wager) + " bet pays total of " + str(round(algo.max_amount + algo.total_wager, 2)) + " for profit of " + str(round(algo.max_amount, 2)))
        
    # else:
    #     print("no profit to bet found")
    # dfManager.parse_valid_bets()
                
if __name__ == "__main__":
    main()