import requests

class EndPoint:
    
    def __init__(self, baseUrl):
        self.m_baseUrl = baseUrl
        self.m_endpointUrl = None
        self.m_parameters = None
        
    def setEndpointUrl(self, url):
        self.m_endpointUrl = url
        
    def setParameters(self, params):
        self.m_parameters = params
        
    def get(self):
        try:
            response = requests.get(self.m_baseUrl + self.m_endpointUrl, params=self.m_parameters)
            return response.json()
        except:
            print('Error with following GET request')
            print('URL: ' + self.m_baseUrl + self.m_endpointUrl)
            print('Params: ' + repr(self.m_parameters))
            return 0 
        