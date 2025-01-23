from typing import List, Tuple, Dict
from dateutil import parser, tz
from datetime import datetime
import math


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
        date = parser.parse(self.last_update).astimezone(SingleBet.TIME_ZONE).strftime("%m/%d %I:%M:%S %p")
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
    def __init__(self, bet: SingleBet, spendAmount: float):
        super().__init__(bet.game_id, bet.commence_time, bet.last_update, bet.bookmaker, bet.betType, bet.name, bet.description, bet.price, bet.point)
        self.spend_amount = round(spendAmount, 2)
        
    def __str__(self) -> str:
        price_str = ""
        if self.price > 0:
            price_str = "+" + str(self.price)
        else:
            price_str = str(self.price)
        date = parser.parse(self.last_update).astimezone(SingleBet.TIME_ZONE).strftime("%m/%d %I:%M:%S %p")
        bt = NAME_CONDENSER[self.betType]
        return f'{self.bookmaker} :: {bt} :: {date} :: {self.description} {str(self.point)} for {self.name} @ {price_str}: ${str(self.spend_amount)}'

    def __eq__(self, other):
        if isinstance(other, WinningBet):
            return ((self.game_id == other.game_id) and (self.betType == other.betType) and (math.isclose(self.price,other.price)) and (math.isclose(self.point,other.point)) and (self.bookmaker == other.bookmaker))
        return False
    
class WinningBetScenario:
    def __init__(self, bet1: WinningBet, bet2: WinningBet, totalWager: int, totalProfit: float):
        self.bet1 = bet1
        self.bet2 = bet2
        self.totalWager = totalWager
        self.totalProfit = round(totalProfit,2)
    
    def __eq__(self, other):
        if isinstance(other, WinningBetScenario):
            if (self.bet1 == other.bet1):
                return ((self.bet2 == other.bet2) and (math.isclose(self.totalProfit, other.totalProfit)))
            elif (self.bet1 == other.bet2):
                return ((self.bet2 == other.bet1) and (math.isclose(self.totalProfit, other.totalProfit)))
            elif (self.bet2 == other.bet1):
                return ((self.bet1 == other.bet2) and (math.isclose(self.totalProfit, other.totalProfit)))
        return False
    
class ArbitrageAlgorithm:
    def __init__(self, totalWager: int):
        self.total_wager: int = totalWager
        self.valid_bets: Dict[str, List[Tuple[SingleBet, List[SingleBet]]]]= []
        self.winning_bets : List[WinningBetScenario] = []
        
    def setTotalWager(self, totalWager: int):
        self.total_wager = totalWager
        
    def _american_to_decimal(self, american_odds):
        if american_odds > 0:
            return (american_odds/100) + 1
        return (100/abs(american_odds)) + 1
    
    def _isBetOld(self, bet: SingleBet):
        timeOld = parser.parse(bet.last_update).astimezone(SingleBet.TIME_ZONE).timestamp()
        timeNow =  datetime.now().astimezone(SingleBet.TIME_ZONE).timestamp()

        minutes = 2.5

        # return true on bets older than 2.5 minutes...
        # this most likely means the bet is not available
        return ((timeNow - timeOld) > (60.0 * minutes))

    def find_profit(self, bets: Dict[str,List[Tuple[SingleBet, List[SingleBet]]]]):
        self.valid_bets = bets
        self.win_profit = 0
        self.winning_bets = []
        for player in self.valid_bets.keys():
            for valid_bets in self.valid_bets[player]:
                bet1 = valid_bets[0]
                
                for vb in valid_bets[1]:
                    bet2 = vb
                    if (not self._isBetOld(bet1)) and (not self._isBetOld(bet2)):
                        self._get_potential_gain(bet1, bet2)
                    
    def _round_numbers(self, num: float, roundUp: str) -> int:
        abs_number = abs(num)
        func = math.ceil if roundUp == "up" else math.floor if roundUp == "down" else round

        num_digits = len(str(int(abs_number)))
        res = 0

        if num_digits <= 2:
            res = num
        elif num_digits == 3:
            res = func(num / 10) * 10
        elif num_digits == 4:
            res = func(num / 50) * 50
        elif num_digits == 5:
            res = func(num / 100) * 100
        else:
            res = func(num / 1000) * 1000

        return res

    def _get_potential_gain(self, b1: SingleBet, b2: SingleBet):
        
        win_profit = 0
        win_bet1_spend = 0
        win_bet2_spend = 0

        bet1_decimal = self._american_to_decimal(b1.price)
        bet2_decimal = self._american_to_decimal(b2.price)
        
        # If sum of inverses >= 1, not possible for arbitrage
        if (1 / bet1_decimal) + (1/ bet2_decimal) >= 1:
            return
        
        # fractional amounts on each outcome
        bet1_spend = self.total_wager * (1/bet1_decimal) / ((1 /bet1_decimal)+(1/bet2_decimal))
        bet2_spend = self.total_wager * (1/bet2_decimal) / ((1 /bet1_decimal)+(1/bet2_decimal))
        
        # round numbers and find profit...
        # 2 scenarios
        # -> round bet1 up and bet2 down
        # -> round bet1 down and bet2 up
        for i in range(2):
            b1_spend = 0
            b2_spend = 0
            # round bet 1 up, bet 2 down...
            if i == 0:
                b1_spend = self._round_numbers(bet1_spend, "up")
                b2_spend = self._round_numbers(bet2_spend - (b1_spend - bet1_spend), "close")

                if ((b1_spend + b2_spend) > self.total_wager):
                    b2_spend = self._round_numbers(bet2_spend- (b1_spend - bet1_spend), "down")

            # round bet 1 down, bet 2 up...
            else:
                b2_spend = self._round_numbers(bet2_spend, "up")
                b1_spend = self._round_numbers(bet1_spend - (b2_spend - bet2_spend), "close")

                if ((b1_spend + b2_spend) > self.total_wager):
                    b1_spend = self._round_numbers(bet1_spend - (b2_spend - bet2_spend), "down")

            bet1_profit = (b1_spend * (bet1_decimal - 1)) + b1_spend
            bet2_profit = (b2_spend * (bet2_decimal - 1)) + b2_spend
            temp_profit = round(min(bet1_profit, bet2_profit), 2)
            if temp_profit > self.total_wager:
                if temp_profit > win_profit:
                    win_profit = temp_profit
                    win_bet1_spend = b1_spend
                    win_bet2_spend = b2_spend
        
        
        if round((win_profit - float(self.total_wager)), 2) > 0.0:
            # if we encounter a scenario with greater than 30% profit (ex: 500 pays 150)
            # we are likely viewing live data that has not been updated... maybe somebody just
            # hit a 3, made an assist, scored a bucket, etc. and only 1 book maker has reflected this change.
            # Lets ignore this data because when we go to place the bet, it will have
            # changed and will no longer be valid
            #
            # Bets with 30% profit or less are more likely to be captured
            if (round(win_profit - float(self.total_wager), 2) < (round(0.3 * self.total_wager, 2))):
                self.winning_bets.append(
                    WinningBetScenario(
                        WinningBet(b1, win_bet1_spend),
                        WinningBet(b2, win_bet2_spend),
                        self.total_wager,
                        round(win_profit - float(self.total_wager), 2)
                    )
                )