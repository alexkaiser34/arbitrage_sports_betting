
class TestAlgorithm:
    
    def __init__(self, total_wager: int, bet1_odds: int, bet2_odds: int):
        self.total_wager = total_wager
        self.bet1_odds = bet1_odds
        self.bet2_odds = bet2_odds
        self.win_bet1 = float(0)
        self.win_bet2 = float(0)
        self.win_profit = float(0)
    
    def _american_to_decimal(self, american_odds):
        if american_odds > 0:
            return (american_odds/100) + 1
        return float((100/abs(american_odds)) + 1)
        
    def run_algorithm(self):
        bet1_decimal = self._american_to_decimal(self.bet1_odds)
        bet2_decimal = self._american_to_decimal(self.bet2_odds)
        
        # If sum of inverses >= 1, not possible for arbitrage
        if (1 / bet1_decimal) + (1/ bet2_decimal) >= 1:
            self.win_bet1 = 0
            self.win_bet2 = 0
            self.win = 0
            return
        
        # fractional amounts on each outcome
        bet1_spend = self.total_wager * (1/bet1_decimal) / ((1 /bet1_decimal)+(1/bet2_decimal))
        bet2_spend = self.total_wager * (1/bet2_decimal) / ((1 /bet1_decimal)+(1/bet2_decimal))
        
        # minimum guarenteed profit
        bet1_profit = (bet1_spend * (bet1_decimal - 1)) + bet1_spend
        bet2_profit = (bet2_spend * (bet2_decimal - 1)) + bet2_spend
        
        self.win_profit = round(min(bet1_profit, bet2_profit), 2)
        self.win_bet1 = round(bet1_spend, 2)
        self.win_bet2 = round(bet2_spend, 2)
            
    def print_winnings(self):
        if self.win_profit <= 0:
            print("no money can be won")
        else:
            print("\nGUARENTEED MONEY CAN BE MADE\n")
            print("\nBet1: $" + str(self.win_bet1) + " @ " + str(self.bet1_odds))
            print("\nBet2: $" + str(self.win_bet2) + " @ " + str(self.bet2_odds))
            print("\n" + str(self.total_wager) + " bet pays total of " + str(self.win_profit) + " for profit of $" + str(round(self.win_profit - self.total_wager, 2)))