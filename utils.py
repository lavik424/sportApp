
url_type = {'basket' :'https://www.livescore.com/basketball/',
            'foot' :'https://www.livescore.com/',
            'tennis' :'https://www.livescore.com/tennis/'}

SECONDS_TO_WAIT = 10
MAX_ATTEMPTS_ALLOWED = 5
SECONDS = 60
MINUTES = 60
HOURS_ADAY = 24
DELAY = 120

class MyException(Exception):
    def __init__(self,res):
        self.res = res
    def __str__(self):
        repr(self.res)