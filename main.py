from app import App
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sport", help="Specify which sport you are looking at (basketball or football)", type=str)
    parser.add_argument("total_wager", help="Enter an integer for total money to be spent on wagers", type=int)
    args = parser.parse_args() 
    
    sport :App.Sports = None
    if args.sport == "basketball":
        sport = App.Sports.BASKETBALL
    elif args.sport == "football":
        sport = App.Sports.FOOTBALL
    else:
        raise("Invalid sport entered in command line")
    
    app = App(sport, args.total_wager)
    app.run() 


if __name__ == "__main__":
    main()