import math
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

    def _round_numbers(self, num, roundUp):
        abs_number = abs(num)
        func = math.ceil if roundUp == "up" else math.fabs if roundUp == "down" else round

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
                if temp_profit > self.win_profit:
                    self.win_profit = temp_profit
                    self.win_bet1 = b1_spend
                    self.win_bet2 = b2_spend

    def print_winnings(self):
        if self.win_profit <= 0:
            print("no money can be won")
        else:
            print("\nGUARENTEED MONEY CAN BE MADE\n")
            print("\nBet1: $" + str(self.win_bet1) + " @ " + str(self.bet1_odds))
            print("\nBet2: $" + str(self.win_bet2) + " @ " + str(self.bet2_odds))
            print("\n" + str(self.total_wager) + " bet pays total of " + str(self.win_profit) + " for profit of $" + str(round(self.win_profit - self.total_wager, 2)))