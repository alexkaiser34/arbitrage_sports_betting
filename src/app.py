from odds_api import OddsAPI
from DfManager import DfManager
from ArbitrageAlgorithm import ArbitrageAlgorithm, WinningBet, SingleBet, WinningBetScenario
from enum import Enum
from typing import List, Dict
from models.upcoming_events_response import UpcomingEventsEndResponse
from pushover import PushoverNotifications

class App:
    # sports we care about, see a full list of supported sports in
    # examples/available_sports.json
    SUPPORTED_SPORTS=[
        "americanfootball_nfl", 
        "basketball_nba",
        "baseball_mlb"
    ]
    
    class Sports(Enum):
        FOOTBALL = 0
        BASKETBALL = 1
        BASEBALL = 2
    
    def __init__(self, sport:str, totalWager: int, bookmakers: str, regions: str):
        self.m_sport: List[str] = [x.strip() for x in sport.split(',')]
        self.m_totalWager = totalWager
        self.m_oddsApi: OddsAPI = OddsAPI(self.m_sport, bookmakers, regions)
        self.m_pushover = PushoverNotifications()
        
        self.apiData: Dict[str, List[str]] = {}
        self.wins: List[WinningBetScenario] = []
        self.highestWin: WinningBetScenario = None
    
    def run(self):
        print('\n-------------- BEGIN GRABBING API DATA  ---------------\n')
        self.getPlayerProps()
        print('\n-------------- END GRABBING API DATA ---------------\n')
        print('\n-------------- START ALGORITHM ---------------\n')
        self.runAlgorithm()
        print('\n-------------- END ALGORITHM ---------------\n')
        print('\n-------------- RESULTS ---------------\n')
        self.print_winnings()
        
    def getPlayerProps(self):
        self.apiData.clear()
        self.m_oddsApi.getPlayerProps()
        for sport in self.m_sport:
            self.apiData[sport] = self.m_oddsApi.response_data[sport]
        
    def remove_dup_wins(self):
        temp = []
        
        for win in self.wins:
            if win not in temp:
                temp.append(win)
                
        self.wins = temp
    
    def runAlgorithm(self):
        
        algo = ArbitrageAlgorithm(self.m_totalWager)
        
        self.wins = []
        
        for sport in self.m_sport:
            # each "data" should correspond to player props
            # for one single game
            for data in self.apiData[sport]:
                # create the dataframe for eacb game
                dfMan = DfManager(data, sport)
                
                # find the valid bets
                dfMan.create_valid_bets()
                
                # run the algorithm
                algo.find_profit(dfMan.m_valid_bets)
                win = algo.get_winning_data()
                if win is not None:
                    self.wins.append(win)

        self.remove_dup_wins()
        # get the highest win
        self.highestWin = self._getHighestWin(self.wins)
        
    def find_game(self, bet: WinningBet) -> UpcomingEventsEndResponse:
        for game in self.m_oddsApi.games:
            if game.id == bet.game_id:
                return game
                
    def print_winnings(self):
        if len(self.wins) <= 0:
            print("\nno profit to bet found\n")
        else:
            print("\nWe have found a profit....")
            for win in self.wins:
                print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
                self.print_bet_scenario(win)
            
            print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
            print('-------------- HIGHEST PROFIT BET ---------------')
            self.print_bet_scenario(self.highestWin)
            self.sendHighestWinNotification()
    
    
    def sendHighestWinNotification(self):
        # only send notification when we have a 2% or higher profit
        # Example: 500 * 0.02 = 10, only notify us when we have a profit >= 10
        if (float(self.highestWin.totalProfit) > float(0.02 * self.highestWin.totalWager)):
            winningGame = self.find_game(self.highestWin.bet1)
            title = ""
            if not winningGame.upcoming:
                title = "LIVE: " + str(winningGame)
            else:
                title = str(winningGame)
            message = f'{str(self.highestWin.bet1)}\n\n{str(self.highestWin.bet2)}\n\n${str(self.highestWin.totalWager)} wager = ${str(round(float(self.highestWin.totalProfit), 2))} profit'
            self.m_pushover.sendMessage(title, message)
        
        
    def print_bet_scenario(self, betScenario: WinningBetScenario):
        winningGame = self.find_game(betScenario.bet1)
        
        print("\n--------------- GAME INFO -----------\n")
        print(winningGame)
        print("\n--------------- BET 1 ---------------\n")
        print(betScenario.bet1)
        print("\n--------------- BET 2 ---------------\n")
        print(betScenario.bet2)
        print("\n--------------- TOTAL WINNINGS ---------------\n")
        print("$" + str(betScenario.totalWager) + " bet pays total of $" + str(round(float(betScenario.totalWager) + float(betScenario.totalProfit), 2)) + " for profit of $" + str(round(float(betScenario.totalProfit), 2)) + "\n")
            
        
    def _getHighestWin(self, wins: List[WinningBetScenario]) -> WinningBetScenario:
        if len(wins) <= 0:
            return None
        
        maxProfit:float = max([float(win.totalProfit) for win in wins])
        for win in wins:
            if abs(float(win.totalProfit) - maxProfit) < 0.001:
                return win