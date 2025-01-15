import requests
from requests import Response

class PushoverNotifications:
  
  TOKEN="a9vp4513p9rhkyowpfxrryese8yvtb"
  USER="uuqhmv5av9zpjf8eqga1bmh99zeako"
  BASE_URL="https://api.pushover.net/1/messages.json"
  
  def __init__(self):
    self.m_token = PushoverNotifications.TOKEN
    self.m_user = PushoverNotifications.USER
    self.m_baseUrl = PushoverNotifications.BASE_URL

  def sendMessage(self, title: str, message: str, priority=0):
    data = {
      "token": self.m_token,
      "user": self.m_user,
      "ttl": 3600,
      "title": title,
      "priority": priority,
      "message": message
    }
    
    r = requests.post(self.m_baseUrl, data=data)
    return r.status_code
    
