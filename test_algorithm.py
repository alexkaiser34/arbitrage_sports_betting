
class TestAlgorithm:
    
    def __init__(self, total_wager: int, bet1_odds: int, bet2_odds: int):
        self.total_wager = total_wager
        self.bet1_odds = bet1_odds
        self.bet2_odds = bet2_odds
        self.max_amount = 0
        self.win_bet1 = 0
        self.win_bet2 = 0
        self.win_profit = 0
    
    def _american_to_decimal(self, american_odds):
        if american_odds > 0:
            return (american_odds/100) + 1
        return (100/abs(american_odds)) + 1
        
    def run_algorithm(self):
        bet1_decimal = self._american_to_decimal(self.bet1_odds)
        bet2_decimal = self._american_to_decimal(self.bet2_odds)
        
        self.max_amount = 0
        self.win_bet1 = 0
        self.win_bet2 = 0
        self.win_profit = 0
        
        prev_max = 0

        for i in range(1, self.total_wager):
            bet1_spend = i
            bet2_spend = self.total_wager - i
            iteration_profit = 0
            
            bet1_gain = (bet1_spend * bet1_decimal) - self.total_wager
            bet2_gain = (bet2_spend * bet2_decimal) - self.total_wager
            
            if (bet1_gain > 0) and (bet2_gain > 0):
                iteration_profit = min(bet1_gain, bet2_gain)
                
            if iteration_profit > 0:
                self.max_amount = max(iteration_profit, self.max_amount)
                if self.max_amount != prev_max:
                    self.win_bet1 = bet1_spend
                    self.win_bet2 = bet2_spend
                    self.win_profit = self.max_amount
                
            prev_max = self.max_amount
    
    def print_winnings(self):
        if self.max_amount <= 0:
            print("no money can be won")
        else:
            print("\nGUARENTEED MONEY CAN BE MADE\n")
            print("\nBet1: $" + str(self.win_bet1) + " @ " + str(self.bet1_odds))
            print("\nBet2: $" + str(self.win_bet2) + " @ " + str(self.bet2_odds))
            print("\n" + str(self.total_wager) + " bet pays total of " + str(round(self.max_amount + self.total_wager, 2)) + " for profit of $" + str(round(self.max_amount, 2)))