
class AvailableSportResponse:
    
    def __init__(self, key: str, group: str, title: str, active: bool):
        self.key = key
        self.group = group
        self.title = title
        self.active = active
        
    def __str__(self):
        return f'\nkey={self.key}, group={self.group}, title={self.title}, active={str(self.active)}\n'