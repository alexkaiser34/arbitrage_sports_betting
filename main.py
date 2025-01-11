from app import App
import argparse
import json
from typing import Dict, Tuple
from test_algorithm import TestAlgorithm

VALID_APP_TYPES = [ "main", "test" ]

def parse_arguments():
    parser = argparse.ArgumentParser()
    # parser.add_argument("sport", help="Specify which sport you are looking at (basketball or football)", type=str)
    parser.add_argument("app_type", help="Enter application type (main or test)", type=str)
    args = parser.parse_args()
    
    if not args.app_type:
        print("ERROR: No application type specified - You need the app_type argument")
        exit(0)
    elif args.app_type not in VALID_APP_TYPES:
        print(f'ERROR: {args.app_type} is not a valid application type. Valid types are main or test')
        exit(0)
    
    return args

def read_config(args) -> Tuple[str, Dict]:
    # read config data (app_config,json)
    config_data = None

    with open('./app_config.json', 'r') as file:
        config_data = json.load(file)
        
    if args.app_type == "main":
        return "main", config_data['main_app']

    return "test", config_data['test_algorithm']    

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
    args = parse_arguments()
    app_type, config = read_config(args)
    
    if app_type == "main":
        handle_main(config)
    else:
        handle_test(config)


if __name__ == "__main__":
    main()