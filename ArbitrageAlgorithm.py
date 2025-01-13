from typing import List, Tuple, Dict
from dateutil import parser, tz
from datetime import datetime


NAME_CONDENSER = {
    "batter_home_runs": "HR",
    "batter_hits": "hits",
    "batter_total_bases": "tot bases",
    "batter_rbis" : "RBIs",
    "batter_runs_scored": "runs",
    "batter_hits_runs_rbis" : "runs/RBIs",
    "batter_walks" : "walks",
    "batter_stolen_bases": "stolen bases",
    "pitcher_strikeouts" : "SOs",
    "pitcher_hits_allowed" : "pitcher hits alwd",
    "pitcher_walks" : "pitcher walks",
    "pitcher_earned_runs" : "pitcher ER",
    "pitcher_outs" : "pitcher outs",
    "batter_total_bases_alternate" : "tot bases alt",
    "batter_home_runs_alternate" : "HR alt",
    "batter_hits_alternate": "hits alt",
    "batter_rbis_alternate": "RBIs alt",
    "pitcher_hits_allowed_alternate": "pitcher hits alwd alt",
    "pitcher_walks_alternate" : "pitcher walks alt",
    "pitcher_strikeouts_alternate" : "SOs alt",
    "player_points": "points",
    "player_rebounds" : "REB",
    "player_assists": "AST",
    "player_threes": "threes",
    "player_field_goals" : "FG",
    "player_double_double" : "double-double",
    "player_triple_double" : "triple-double",
    "player_points_rebounds" : "PR",
    "player_points_assists" : "PA",
    "player_rebounds_assists" : "RA",
    "player_points_alternate" : "points alt",
    "player_rebounds_alternate": "REB alt",
    "player_assists_alternate" : "AST alt",
    "player_threes_alternate" : "threes alt",
    "player_points_rebounds_assists" : "PRA",
    "player_points_assists_alternate" : "PA alt",
    "player_points_rebounds_alternate" : "PR alt",
    "player_rebounds_assists_alternate" : "RA alt",
    "player_points_rebounds_assists_alternate" : "PRA alt",
    "player_pass_tds" : "pass TD",
    "player_pass_yds" : "pass yds",
    "player_reception_yds" : "rec yds",
    "player_rush_yds" : "rush yds",
    "player_tds_over" : "tds",
    "player_anytime_td" : "anytime td",
    "player_field_goals_alternate" : "FG alt",
    "player_pass_tds_alternate" : "pass TD alt",
    "player_pass_yds_alternate" : "pass yds alt",
    "player_reception_yds_alternate" : "rec yds alt",
    "player_rush_yds_alternate" : "rush yds alt",
    "player_rush_longest_alternate" : "long rush alt",
    "player_rush_longest" : "long rush",
    "player_reception_longest" : "long rec",
    "player_reception_longest_alternate" : "long rec alt",
    "player_rush_attempts" : "# rushes",
    "player_rush_attempts_alternate" : "# rushes alt",
    "player_pass_attempts" : "# passes",
    "player_pass_attempts_alternate" : "# passes alt",
    "player_receptions" : "# rec",
    "player_receptions_alternate" : "# rec alt"
}

class SingleBet:
    TIME_ZONE = tz.gettz('America/New_York')
    def __init__(self, game_id, commence_time, last_update, bookmaker, betType, name, description, price, point):
        self.game_id = game_id
        self.commence_time = commence_time
        self.last_update = last_update
        self.bookmaker = bookmaker
        self.betType = betType
        self.name = name
        self.description = description
        self.price = price
        self.point = point
        
    def __str__(self) -> str:
        date = parser.parse(self.last_update).astimezone(SingleBet.TIME_ZONE).strftime("%m/%d %I:%M %p")
        return f'{self.bookmaker} : {self.betType} : last updated @ {date} : line {self.description} {str(self.point)} for {self.name} @ {str(self.price)}'

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'commence_time': self.commence_time,
            'last_update': self.last_update,
            'bookmaker': self.bookmaker,
            'betType': self.betType,
            'name': self.name,
            'o/u': self.description,
            'price': self.price,
            'point': self.point
        }

class WinningBet(SingleBet):
    def __init__(self, bet: SingleBet, spendAmount: int):
        super().__init__(bet.game_id, bet.commence_time, bet.last_update, bet.bookmaker, bet.betType, bet.name, bet.description, bet.price, bet.point)
        self.spend_amount = spendAmount
        
    def __str__(self) -> str:
        price_str = ""
        if self.price > 0:
            price_str = "+" + str(self.price)
        else:
            price_str = str(self.price)
        date = parser.parse(self.last_update).astimezone(SingleBet.TIME_ZONE).strftime("%m/%d %I:%M %p")
        bt = NAME_CONDENSER[self.betType]
        return f'{self.bookmaker} :: {bt} :: {date} :: {self.description} {str(self.point)} for {self.name} @ {price_str}: ${str(self.spend_amount)}'
        
class WinningBetScenario:
    def __init__(self, bet1: WinningBet, bet2: WinningBet, totalWager: int, totalProfit: float):
        self.bet1 = bet1
        self.bet2 = bet2
        self.totalWager = totalWager
        self.totalProfit = totalProfit
        
    
class ArbitrageAlgorithm:
    def __init__(self, totalWager: int):
        self.total_wager: int = totalWager
        self.valid_bets: Dict[str, List[Tuple[SingleBet, List[SingleBet]]]]= []
        self.max_amount: int = 0
        self.prev_max: int = 0
        self.bet1: WinningBet = None
        self.bet2: WinningBet = None
        
    def setTotalWager(self, totalWager: int):
        self.total_wager = totalWager
        
    def _american_to_decimal(self, american_odds):
        if american_odds > 0:
            return (american_odds/100) + 1
        return (100/abs(american_odds)) + 1
        
    
    def find_profit(self, bets: Dict[str,List[Tuple[SingleBet, List[SingleBet]]]]):
        self.valid_bets = bets
        self.max_amount = 0
        self.prev_max = 0
        
        for player in self.valid_bets.keys():
            
            for valid_bets in self.valid_bets[player]:
                bet1 = valid_bets[0]
                
                for vb in valid_bets[1]:
                    bet2 = vb
                    self._get_potential_gain(bet1, bet2)
                    
                    
    def _get_potential_gain(self, b1: SingleBet, b2: SingleBet):
        b1_dec_odds = self._american_to_decimal(b1.price)
        b2_dec_odds = self._american_to_decimal(b2.price)
        
        b1_spend = 0
        b2_spend = 0
        
        for i in range(1, self.total_wager):
            
            b1_spend = i
            b2_spend = self.total_wager - i
            iteration_profit = 0
            
            b1_gain = (b1_spend * b1_dec_odds) - self.total_wager
            b2_gain = (b2_spend * b2_dec_odds) - self.total_wager
            
            
            if (b1_gain > 0) and (b2_gain > 0):
                iteration_profit = min(b1_gain, b2_gain)
            
            if iteration_profit > 0:
                self.max_amount = max(iteration_profit, self.max_amount)
                if self.max_amount != self.prev_max:
                    self.bet1 = WinningBet(b1, b1_spend)
                    self.bet2 = WinningBet(b2, b2_spend)
                    
            
            self.prev_max = self.max_amount
    
    def get_winning_data(self) -> WinningBetScenario:
        if self.max_amount > 0:
            return WinningBetScenario(
                self.bet1,
                self.bet2,
                self.total_wager,
                str(round(self.max_amount, 2))
            )
        
        return None