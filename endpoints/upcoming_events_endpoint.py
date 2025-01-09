from endpoints.base_endpoint import BaseEndpoint
from models.upcoming_events_response import UpcomingEventsEndResponse
from typing import List
import json

# ## if we want to filter commenceTimeTo and commenceTimeFrom optional parameters
# import datetime
# datetime.datetime.now().replace(microsecond=0).isoformat()

class UpcomingEventsEndpoint(BaseEndpoint):
    
    def __init__(self, baseUrl: str, apiKey: str, sport: str):
        super().__init__(baseUrl, apiKey)
        self.sport = sport
        self.result : List[UpcomingEventsEndResponse] = []
        self.setEndpointUrl('/sports/' + self.sport + '/events')
        self.setParameters({'apiKey': self.apiKey})
    
    def get(self):
        json_response = super().get()
        self._store_results(json_response)

    def _store_results(self, response):
        self.result = []
        j = json.loads(response)
        
        for item in j:
            temp = UpcomingEventsEndResponse(
                item['id'],
                item['sport_key'],
                item['sport_title'],
                item['commence_time'],
                item['home_team'],
                item['away_team']
            )
            self.result.append(temp)
            
    def print_results(self):
        for result in self.result:
            print(result)