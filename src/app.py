from odds_api import OddsAPI
from DfManager import DfManager
from ArbitrageAlgorithm import ArbitrageAlgorithm, WinningBet, SingleBet, WinningBetScenario
from enum import Enum
from typing import List, Dict
from models.upcoming_events_response import UpcomingEventsEndResponse
from pushover import PushoverNotifications
import concurrent.futures


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
    
    def __init__(self, live_enabled: bool, sport:str, totalWager: int, bookmakers: str, regions: str):
        self.m_sport: List[str] = [x.strip() for x in sport.split(',')]
        self.m_totalWager = totalWager
        self.m_oddsApi: OddsAPI = OddsAPI(live_enabled, self.m_sport, bookmakers, regions)
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
            if sport in self.m_oddsApi.response_data.keys():
                self.apiData[sport] = self.m_oddsApi.response_data[sport]
        
    def remove_dup_wins(self):
        self.wins = list(set(self.wins))

    def sort_wins(self):
        self.wins.sort(key=lambda x: x.totalProfit, reverse=True)
        
    def runAlgoByPlayerProps(self, sport: str, playerProps: str) -> List[WinningBetScenario]:
        algo = ArbitrageAlgorithm(self.m_totalWager)
        
        # create the dataframe for each game
        dfMan = DfManager(playerProps, sport)
                
        # find the valid bets
        dfMan.create_valid_bets()
                
        # run the algorithm
        algo.find_profit(dfMan.m_valid_bets)

        return algo.winning_bets

    def runAlgoBySport(self, sport: str):
        if sport in self.apiData.keys():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.runAlgoByPlayerProps, sport, data) for data in self.apiData[sport]]
                for future in concurrent.futures.as_completed(futures):
                    winning_bets = future.result()
                    self.wins.extend(winning_bets)

    def runAlgorithm(self):
        self.wins = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.runAlgoBySport, sport) for sport in self.m_sport]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        self.remove_dup_wins()
        self.sort_wins()

        # get the highest win
        if len(self.wins) > 0:
            self.highestWin = self.wins[0]
        
    def find_game(self, bet: WinningBet) -> UpcomingEventsEndResponse:
        return next((game for game in self.m_oddsApi.games if game.id == bet.game_id), None)
                
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
            self.sendWinNotifications()
    
    
    def sendWinNotifications(self):
        message = ''
        title = ''
        priority = 0

        for winCount, win in enumerate(self.wins):
            # only send games with 2% or more profit
            # We should not receive profit more than 6%
            shouldSendMessage =  (float(win.totalProfit) > float(0.02 * win.totalWager))
            if shouldSendMessage:
                # game object
                winningGame = self.find_game(win.bet1)

                # highest win, make title
                if winCount == 0:
                    if not winningGame.upcoming:
                        title = "LIVE: " + str(winningGame)
                    else:
                        title = str(winningGame)
                    message += f'{str(win.bet1)}\n\n{str(win.bet2)}\n\n${str(win.totalWager)} wager = ${str(round(float(win.totalProfit), 2))} profit'

                # next 2 highest wins
                elif winCount < 3:
                    game_str = ""
                    if not winningGame.upcoming:
                        game_str = "LIVE: " + str(winningGame)
                    else:
                        game_str = str(winningGame)

                    message += f'\n\n++++++++++ BET OPTION {str(winCount + 1)} ++++++++++\n\n'
                    message += game_str
                    message += f'\n\n{str(win.bet1)}\n\n{str(win.bet2)}\n\n${str(win.totalWager)} wager = ${str(round(float(win.totalProfit), 2))} profit'

                # mark message as high priority when profit is greater than 5 percent and game is upcoming
                isHighPriority = ((float(win.totalProfit) > float(0.05 * win.totalWager)) and winningGame.upcoming)
                if isHighPriority:
                    priority = 1

        # send message if it is not empty
        if message != '':
            self.m_pushover.sendMessage(title, message, priority)
        
        
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