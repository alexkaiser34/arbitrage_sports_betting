from app import App
from typing import Dict
from test_algorithm import TestAlgorithm


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

def main():
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