from app import App
from typing import Dict
from test_algorithm import TestAlgorithm
import sys

def handle_test(config: Dict):
    testAlgo = TestAlgorithm(
        config['total_wager'],
        config['bet1_odds'],
        config['bet2_odds']
    )
    testAlgo.run_algorithm()
    testAlgo.print_winnings()
    
def handle_main(config: Dict):
    sport :App.Sports = None
    
    if config['sport'] == "basketball":
        sport = App.Sports.BASKETBALL
    elif config['sport'] == "football":
        sport = App.Sports.FOOTBALL
    else:
        raise("Invalid sport entered in command line")
    
    app = App(
        sport,
        config['total_wager'],
        config['bookmakers'],
        config['regions']
    )

    app.run()
    
def american_to_decimal(american_odds):
        if american_odds > 0:
            return (american_odds/100) + 1
        return float((100/abs(american_odds)) + 1)
    
def handle_reverse():
    b1_odds = int(input("Please enter bet 1 odds: "))
    b1_spend = int(input("Please enter bet 1 spend amount: "))
    b1_decimal = american_to_decimal(b1_odds)
    
    b2_odds = int(input("Please enter bet 2 odds: "))
    b2_spend = int(input("Please enter bet 2 spend amount: "))
    b2_decimal = american_to_decimal(b2_odds)
    
    
    # minimum guarenteed profit
    bet1_profit = (b1_spend * b1_decimal)
    bet2_profit = (b2_spend * b2_decimal)
    
    win_profit = round(min(bet1_profit, bet2_profit), 2)
    
    if win_profit > (b1_spend + b2_spend):
        print("\nGUARENTEED MONEY CAN BE MADE\n")
        print("\nBet1: $" + str(b1_spend) + " @ " + str(b1_odds) + " = " + str(round(bet1_profit,2)))
        print("\nBet2: $" + str(b2_spend) + " @ " + str(b2_odds) + " = " + str(round(bet2_profit,2)))
        print("\n" + str(b1_spend + b2_spend) + " bet pays total of " + str(win_profit) + " for profit of $" + str(round(win_profit - (b1_spend + b2_spend), 2)))
    else:
        print('not possible to make money')
        
    
    

def main():
    reverse = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "reverse":
            reverse = True
            
    if reverse:
        handle_reverse()
    else:
        wager=int(input('Please enter a wager: '))
        b1_odds=int(input('Please enter bet1 odds: '))
        b2_odds=int(input('Please enter bet2 odds: '))
        
        testAlgo = TestAlgorithm(
            total_wager=wager,
            bet1_odds=b1_odds,
            bet2_odds=b2_odds
        )
        
        testAlgo.run_algorithm()
        testAlgo.print_winnings()


if __name__ == "__main__":
    main()