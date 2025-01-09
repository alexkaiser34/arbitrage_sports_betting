import json
import pandas as pd

class SingleBet:
    
    def __init__(self, bookmaker, betType, name, description, price, point):
        self.bookmaker = bookmaker
        self.betType = betType
        self.name = name
        self.description = description
        self.price = price
        self.point = point
        
    def __str__(self) -> str:
        return f'{self.bookmaker} = {self.betType} : line {self.description} {str(self.point)}  for {self.name} @ {str(self.price)}'
         

def create_df(fileName):
    

def get_bets(df):
    bets = []
    for bookmaker in df['bookmakers']:
        bookmakerTitle = bookmaker['key']
        for market in bookmaker['markets']:
            bet_type = market['key']
            for outcome in market['outcomes']:
                if "point" in outcome:
                    s1 = SingleBet(bookmakerTitle, bet_type, outcome['description'], outcome['name'], outcome['price'], outcome['point'])
                    bets.append(s1)
    return bets

def parseBetsByName(bets):
    s = set()
    for bet in bets:
        if bet.name not in s:
            s.add(bet.name)
            
    result = {}
    for name in s:
        result[name] = [bet for bet in bets if bet.name == name]
    return result

def find_valid_bets(betsByName):
    valid_bets = {}
    # go through each player
    for key in betsByName.keys():
        
        playerBetDictionary = {}
        # grab the unique player bet types available
        betTypeSet = set()
        for bet in betsByName[key]:
            if bet.betType not in betTypeSet:
                betTypeSet.add(bet.betType)
                
        for betType in betTypeSet:
            playerBetDictionary[betType] = [bet2 for bet2 in betsByName[key] if bet2.betType == betType]
            
        temp_valid = []
        
        for betType2 in playerBetDictionary.keys():
            for betItem in playerBetDictionary[betType2]:
                temp = []
                if betItem.description == "Over":
                    temp = [bet3 for bet3 in playerBetDictionary[betType2] if ((bet3.description == "Under") and (abs(bet3.point - betItem.point) <= 0.6))]
                else:
                    temp = [bet3 for bet3 in playerBetDictionary[betType2] if ((bet3.description == "Over") and (abs(bet3.point - betItem.point) <= 0.6))]
                
                if betItem in temp:
                    temp.remove(betItem)
                playerBetDictionary[betType2].remove(betItem)
                    
                if len(temp) > 0:
                    temp_valid.append((betItem, temp))
                    # think about if we want to remove this....
                    # for item2 in temp:
                        # playerBetDictionary[betType2].remove(item2)
        
        valid_bets[key] = temp_valid
    return valid_bets
            
            
                

        
    

# validBetsMaster = {}
# for name in s:
    
#     betsByName = [bet for bet in bets if bet.name == name]
#     betDictionary = {}
#     betTypeSet = set()
#     for bet in betsByName:
#         if bet.betType not in betTypeSet:
#             betTypeSet.add(bet.betType)
    
#     for betType in betTypeSet:
#         betDictionary[betType] = [bet for bet in betsByName if bet.betType == betType]
        
#     validBets = []
    
#     # betDictionary will contain a dictionary where the keys are the bet types... it will only have data for one player at a time
#     # we can compare the data in the arrays for each key in the dictionary...
#     # we will want to compare the overs and unders that are seperated by less than a point
#     for key in betDictionary.keys():
#         betDictionary[key]
#         for bet in betDictionary[key]:
#             temp = []
#             if bet.description == "Over":
#                 temp = [bet2 for bet2 in betDictionary[key] if ((bet2.description == "Under") and (abs(bet2.point - bet.point) <= 0.6))]
#             else:
#                 temp = [bet2 for bet2 in betDictionary[key] if ((bet2.description == "Over") and (abs(bet2.point - bet.point) <= 0.6))]
            
#         #     print('-----------------------------------------------')
#         #     print(f'main bet : {bet}')
#         #     for item in temp:
#         #         print(item)
#         #     break
#         # break
            
#             if len(temp) > 0:
#                 validBets.append((bet, temp))
#                 # betDictionary[key].remove(bet)
                
    
#     validBetsMaster[name] = validBets

# for player in validBetsMaster.keys():
#     for vb in validBetsMaster[player]:
#         print('-----------------------------------------------')
#         print(f'MAIN BET\n\t -- {vb[0]}\n')
#         print('VALID BETS')
#         for v in vb[1]:
#             print(f'\t -- {v}')
        
        
#         # print(f'{bet.bookmaker} = {bet.betType} : line {bet.description} {str(bet.point)}  for {bet.name} @ {str(bet.price)}')
    
    # betsByType = [bet for bet in betsByName where bet.betType]
    # for index, betFilter in enumerate(betsFiltered):
    #     print(index)
    #     #  
    # break

# print(bets)
# betsFiltered = [f'{bet.bookmaker} = {bet.betType} : line {bet.description} {str(bet.point)}  for {bet.name} @ {str(bet.price)}'  for bet in bets if bet.name == "Jordan Poole"]

# for bet in betsFiltered:
#     print(bet)
# result = pd.DataFrame()
# isDone = False
# # make dataframe for each bookmaker, compare at end
# for index, bookmaker_row in df.iterrows():
#     print('---------------------------------------------')
#     # print(bookmaker_row['bookmakers'])
#     bookmaker_df = pd.DataFrame.from_dict(bookmaker_row['bookmakers'])
    
#     if (not isDone) and (bookmaker_df['key'].iloc[0] == 'fanduel'):
#         # print(bookmaker_df)
#         result['fanduel'] = {}
#         for index2, market in bookmaker_df.iterrows():
#             market_odds_df = pd.DataFrame.from_dict(market['markets'])
#             # market_odds_df.reset_index()
#             for index3, outcome in market_odds_df.iterrows():
#                 print('===========================')
#                 if outcome['key'] not in result['fanduel']:
#                     result['fanduel'][outcome['key']] = {}
                    
#                 result['fanduel'][outcome['key']][outcome['outcomes']['description']] = outcome['outcomes']
#                 # player_odds_df = pd.DataFrame.from_dict(outcome['outcomes'])
#                 # print(player_odds_df)
#                 # print(outcome)
#             # if "key1" in d:
#             # outcomes_df = pd.DataFrame.from_dict(market['markets']['outcomes'])
#             # print(outcomes_df)
#             # print(market_odds_df)
#         # markets_df = pd.DataFrame.from_dict(bookmaker_df['markets'])
#         # for index, market in markets_df.iterrows():
#         #     print(market)
#         isDone = True
#     # game_title = bookmaker_row['home_team'] + ' vs ' + bookmaker_row['away_team']
#     # result[bookmaker_df['key'].iloc[0]] = []
    
#     # for index2, odds_row in bookmaker_df.iterrows():
#     #     market_odds_df = pd.DataFrame.from_dict(odds_row['markets'])
#     # # market_odds_df.reset_index()
#     #     print(market_odds_df)
#     # print(game_title)
#     # print(bookmaker_df['key'].iloc[0])

# df_res = pd.DataFrame.from_dict(result)

# print(df_res)
# for key,value in result['fanduel'].items():
#     print(f'{key} : {value}')

# for i
# print(df['bookmakers'])

def main():
    # file = 'examples/wizards_vs_sixers_v2.txt'
    # df = create_df(file)
    # bets = get_bets(df)
    # betsByName = parseBetsByName(bets)
    # valid_bets = find_valid_bets(betsByName)
    
    # # first element is main bet... second element is array of valid bets
    # for player in valid_bets.keys():
    #     print('-----------------------------------------------')
    #     print(f'\t PLAYER = {player}')
        
    #     # array of tuples
    #     for validBet in valid_bets[player]:
    #         # tuple
    #         print("=============================================")
    #         print(f'MAIN BET\n\t -- {validBet[0]}\n')
    #         print('VALID BETS')
    #         for v in validBet[1]:
    #             print(f'\t -- {v}')
    
    file = 'examples/chargers_game_v2.json'
    df = create_df(file)
    print(df)
        
        
    
    
    
    
    
if __name__ == "__main__":
    main()