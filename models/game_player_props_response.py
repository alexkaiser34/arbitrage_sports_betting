from typing import List


class Outcome:
    def __init__(self, name: str, description: str, price: int, point: float):
        self.name = name
        self.description = description
        self.price = price
        self.point = point
        
    def __str__(self):
        return f'name={self.name}, description={self.description}, price={str(self.price)}, point={str(self.point)}'
        
class Market:
    def __init__(self, key: str, last_update: str, outcomes: List[Outcome]):
        self.key = key
        self.last_update = last_update
        self.outcomes = outcomes
        
    def __str__(self):
        return f'market_key={self.key}, last_update={self.last_update}'

class Bookmaker:
    def __init__(self, key: str, markets: List[Market]):
        self.key = key
        self.markets = markets
        
    def __str__(self):
        return f'bookmaker_key={self.key}'


class GamePlayerPropsResponse:
    def __init__(self, id: str, sport_key: str, sport_title: str, commence_time: str, home_team: str, away_team: str, bookmakers: List[Bookmaker]):
        self.id = id
        self.sport_key = sport_key
        self.sport_title = sport_title
        self.commence_time = commence_time
        self.home_team = home_team
        self.away_team = away_team
        self.bookmakers = bookmakers
        
    def __str__(self):
        return f'GameId={self.id}, sport={self.sport_key}, commence_time={self.commence_time}, home_team={self.home_team}, away_team={self.away_team}'