from dateutil import parser, tz
from datetime import datetime, timezone
import ciso8601

class UpcomingEventsEndResponse:

    TIME_ZONE = tz.gettz('America/New_York')
    
    def __init__(self, id: str, sports_key: str, sport_title: str, commence_time: str, home_team: str, away_team: str):
        self.id = id
        self.sports_key = sports_key
        self.sport_title = sport_title
        self.commence_time = commence_time
        self.home_team = home_team
        self.away_team = away_team
        self.upcoming = self._isUpcoming()
        
    def _isUpcoming(self):
        api_time = ciso8601.parse_datetime(self.commence_time).astimezone(UpcomingEventsEndResponse.TIME_ZONE).timestamp()
        now = datetime.now(timezone.utc).astimezone(UpcomingEventsEndResponse.TIME_ZONE).timestamp()
        return (api_time > now)
    
    def updateUpcoming(self):
        self.upcoming = self._isUpcoming()
        
    def __str__(self):
        date = parser.parse(self.commence_time).astimezone(UpcomingEventsEndResponse.TIME_ZONE).strftime("%m-%d %I:%M %p")
        return f'{self.sport_title} - {self.home_team} vs {self.away_team} @ {date}'

    def toDict(self):
        return {
            "id": self.id,
            "sports_key": self.sports_key,
            "sport_title": self.sport_title,
            "commence_time": self.commence_time,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "upcoming": self.upcoming
        }