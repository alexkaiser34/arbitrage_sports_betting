
class UpcomingEventsEndResponse:
    
    def __init__(self, id: str, sports_key: str, sport_title: str, commence_time: str, home_team: str, away_team: str):
        self.id = id
        self.sports_key = sports_key
        self.sport_title = sport_title
        self.commence_time = commence_time
        self.home_team = home_team
        self.away_team = away_team
        
    def __str__(self):
        return f'\nid={self.id}, sport_key={self.sports_key}, sport_title={self.sport_title}, commence_time={self.commence_time}, home_team={self.home_team}, away_team={self.away_team}\n'