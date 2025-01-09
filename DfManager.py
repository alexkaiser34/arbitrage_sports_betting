import pandas as pd
import json


## TO DO: We currently filter the dataframe by bet type...
## However, we want to ensure we look at alternate lines as well in some cases
## Alternate lines will have a different bet type
## We should create some type of map to ensure we compare standard and alternate lines when desired
## May just need to define which markets are considered alternates... we should always be including alternate
## markets with a standard market

##################### DF Schema ##################
# game_id   commence_time   bookmaker  betType  name  O/U  price  point


class SingleBet:
    def __init__(self, game_id, commence_time, bookmaker, betType, name, description, price, point):
        self.game_id = game_id
        self.commence_time = commence_time
        self.bookmaker = bookmaker
        self.betType = betType
        self.name = name
        self.description = description
        self.price = price
        self.point = point
        
    def __str__(self) -> str:
        return f'{self.bookmaker} = {self.betType} : line {self.description} {str(self.point)}  for {self.name} @ {str(self.price)}'

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'commence_time': self.commence_time,
            'bookmaker': self.bookmaker,
            'betType': self.betType,
            'name': self.name,
            'o/u': self.description,
            'price': self.price,
            'point': self.point
        }

class DfManager:
    
    def __init__(self, fileName):
        self.fileName = fileName
        self.initial_df = self.create_df_from_json_file(self.fileName)
        self.df = None
        self.data = []
        self.valid_bets = {}
        self.betTypes = set()
        self.playerNames = set()
        self.bookmakers = set()
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
                
                
    def searchByNames(self):
        # go through each player name and find valid bets...
        for name in self.playerNames:
            filtered_df = self.df[self.df['name'] == name]
            self.find_valid_bets(filtered_df)
            
    def find_valid_bets(self, df):
        for betType in self.betTypes:
            bt_filter = df[df['betType'] == betType]
            if not bt_filter.empty:
                o_filter = bt_filter[bt_filter['o/u'] == 'O']
                u_filter = bt_filter[bt_filter['o/u'] == 'U']
            
                for indexO, overRow in o_filter.iterrows():
                    temp = []
                    found = False
                    
                    for indexU, underRow in u_filter.iterrows():
                        if abs(underRow['point'] - overRow['point']) <= 0.6:
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
                    if found:
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
        

def main():
    dfManager = DfManager('examples/wizards_vs_sixers.json')
    dfManager.searchByNames()    
    
    for player in dfManager.valid_bets.keys():
        print("=============================================")
        print("Bet summary for " + player + "\n")
        
        for valid_bets in dfManager.valid_bets[player]:
            print("+++++++++++++++++++++++++++++++++++")
            print(f'MAIN BET\n\t -- {valid_bets[0]}\n')
            print('VALID BETS')
            for v in valid_bets[1]:
                print(f'\t -- {v}')
                
if __name__ == "__main__":
    main()