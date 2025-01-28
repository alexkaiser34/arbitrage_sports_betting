import requests
import json

class BaseEndpoint:
    
    def __init__(self, baseUrl, apiKey):
        self.m_baseUrl = baseUrl
        self.apiKey = apiKey
        self.m_endpointUrl = None
        self.m_parameters = None
        
    def setEndpointUrl(self, url):
        self.m_endpointUrl = url
        
    def setParameters(self, params):
        self.m_parameters = params
        
    def get(self):
        try:
            response = requests.get(self.m_baseUrl + self.m_endpointUrl, params=self.m_parameters)
            if response.status_code != 200:
                print(f'Error with following GET  - response code{response.status_code}')
                print('URL: ' + self.m_baseUrl + self.m_endpointUrl)
                print('Params: ' + repr(self.m_parameters))
                return ''
            return json.dumps(response.json())
        except:
            print('Error with following GET request')
            print('URL: ' + self.m_baseUrl + self.m_endpointUrl)
            print('Params: ' + repr(self.m_parameters))
            return 0 
        