import requests
r = requests.post("https://api.pushover.net/1/messages.json", data = {
  "token": "a9vp4513p9rhkyowpfxrryese8yvtb",
  "user": "uuqhmv5av9zpjf8eqga1bmh99zeako",
  "message": "alex is a cool kid"
})

