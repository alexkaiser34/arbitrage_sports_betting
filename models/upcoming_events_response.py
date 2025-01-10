from dateutil import parser, tz
from datetime import datetime


class UpcomingEventsEndResponse:

    TIME_ZONE = tz.gettz('America/New_York')
    
    def __init__(self, id: str, sports_key: str, sport_title: str, commence_time: str, home_team: str, away_team: str):
        self.id = id
        self.sports_key = sports_key
        self.sport_title = sport_title
        self.commence_time = commence_time
        self.home_team = home_team
        self.away_team = away_team
        
    def __str__(self):
        date = parser.parse(self.commence_time).astimezone(UpcomingEventsEndResponse.TIME_ZONE).strftime("%Y-%m-%d %H:%M")
        return f'{self.sport_title} - {self.home_team} vs {self.away_team} @ {date}'