from endpoints.base_endpoint import BaseEndpoint
from models.available_sport_response import AvailableSportResponse
from typing import List
import json

class AvailableSportsEndpoint(BaseEndpoint):
    
    def __init__(self, baseUrl, apiKey):
        super().__init__(baseUrl, apiKey)
        self.result : List[AvailableSportResponse] = []
        self.setEndpointUrl('/sports/')
        self.setParameters({'apiKey': self.apiKey})
    
    def get(self):
        json_response = super().get()
        self._store_results(json_response)
        return json_response

    def _store_results(self, response):
        self.result = []
        try:
            j = json.loads(response)

            for item in j:
                temp = AvailableSportResponse(
                    item['key'],
                    item['group'],
                    item['title'],
                    item['active']
                )
                self.result.append(temp)
        except:
            print('Error parsing json')
            
    def print_results(self):
        for result in self.result:
            print(result)