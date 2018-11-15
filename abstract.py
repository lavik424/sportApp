from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from bs4 import BeautifulSoup
import utils
from utils import MINUTES,SECONDS, HOURS_ADAY, DELAY, SECONDS_TO_WAIT, TIEBREAK_SCORE
from datetime import datetime
import sched, time
from utils import MyException

finished_game = ['FT','Postp.','OT','Ret.','W.O.']

class AbstractSport:
    """
    Sport object should include:
    1. url
    2. types of notifications
    3. how to search the desired games

    Class attrs:
    1. url = livescore site to take data from
    2. games_map = map of leagues and their games
    3. game_id = the id of the game the user wants to get notification on
    """

    def __init__(self,sport_type):
        """
        Sport initialization.
        :param sport_type: string indicate one sport.
        """
        self.type = sport_type
        self.check_once = False
        self.url = utils.url_type[sport_type]
        self.games_map = {}
        self.league = ''
        self.game_name = ''
        self.game_id = ''
        self.count_bad_attempts = 0
        self.limits = None
        self.time_list = None
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def get_main_soup(self):
        """

        :return: soup of all the games from livescore site
        """
        chrome_options = Options()
        chrome_options.headless=True
        driver = webdriver.Chrome('C:/chromedriver.exe', options=chrome_options)
        # driver.implicitly_wait(SECONDS_TO_WAIT)
        driver.get(self.url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # print(soup.prettify())
        driver.close()

        soup1 = soup.find(class_=[re.compile("content pb44")])  # main frame
        if soup1 is None:
            soup1 = soup.find(attrs={'data-type': "container"})
        if soup1 is None:
            if self.count_bad_attempts >= utils.MAX_ATTEMPTS_ALLOWED:

                raise MyException(-1) # no connection
            else:
                self.count_bad_attempts += 1
                return self.get_main_soup()
        else:
            self.count_bad_attempts = 0
        return soup1

    def get_all_matches_by_league(self):
        """
        instead of querying the site twice (first leagues and then matches)
        :return: a dict mapping list of matches to their corrspondong league
        """
        raise NotImplementedError

    def get_leagues(self):
        """

        :return: list of leagues/ tournaments
        """
        self.get_all_matches_by_league()
        return sorted(self.games_map.keys())

    def get_games_by_league(self,league):
        """

        :param league: string indicates the league name
        :return: list of games
        """
        self.league = league
        dic = {(''.join(filter(str.isalpha, key))): v for key, v in self.games_map.items()}
        return list(dic[league].keys())


    def set_game_id(self, game_name):
        """
        Get game name for user and set its proper id
        :param game_name:
        :return:
        """
        dic = {(''.join(filter(str.isalpha, key))): v for key, v in self.games_map.items()}
        dic = dic[self.league]
        dic = {(''.join(filter(str.isalpha,key))):v for key,v in dic.items()}
        self.game_id = dic[game_name]


    def query_game(self,wanted_starting_time,wanted_diff=0):
        """
        Query one game
        :return:
        """
        if self.count_bad_attempts >= utils.MAX_ATTEMPTS_ALLOWED:
            raise MyException(False)
        soup = self.get_main_soup()
        game = soup.find(attrs={'data-id':self.game_id})
        if game is None:
            self.count_bad_attempts += 1
            self.query_game(wanted_starting_time,wanted_diff)
        else:
            self.count_bad_attempts = 0
            self.check_conditions_first_time(game,wanted_starting_time,wanted_diff)


    def correct_time(self, game_hour, game_minutes):
        """

        :param game_hour:
        :param game_minutes:
        :return:
        """
        curr_hour = datetime.today().hour
        curr_minutes = datetime.today().minute
        if game_hour < curr_hour: #next day..
            h = HOURS_ADAY - curr_hour
            delay = h*MINUTES*SECONDS-curr_minutes*SECONDS +\
                game_hour*MINUTES*SECONDS+game_minutes*SECONDS
        else: # game on the same day
            delay = (game_hour-curr_hour)*MINUTES*SECONDS +\
                    (game_minutes-curr_minutes)*SECONDS
        return delay


    def check_conditions_first_time(self, game,wanted_starting_time,wanted_diff=0):
        """

        :param game: beautiful soup element, contains info about the game
        :param wanted_starting_time: string
        :param wanted_diff: int
        :return:
        """
        curr_time_game = game.find('span').text
        if ":" in curr_time_game:  # game has not started yet
            game_hour, game_minutes = curr_time_game.split(sep=':')
            game_hour = int(game_hour)
            game_minutes = int(game_minutes)

            start_checking_delay = self.correct_time(game_hour, game_minutes)
            self.scheduler.enterabs(time.time()+start_checking_delay,1,action=self.check_conditions,
                       argument=(wanted_starting_time,wanted_diff))
            self.scheduler.run()
        else:  # game has started already
            self.check_conditions(wanted_starting_time,wanted_diff)

    def check_conditions(self,wanted_starting_time,wanted_diff=0):
        """
        After the game have started. Try to meet the condition after
        :param wanted_diff: int
        :param wanted_starting_time: string
        :return: True if conditions met, False if the game ended w\o
        """
        print(time.ctime())
        if self.count_bad_attempts >= utils.MAX_ATTEMPTS_ALLOWED:
            raise MyException(False)
        soup = self.get_main_soup()
        game = soup.find(attrs={'data-id':self.game_id})
        if game.find(class_='row-group live') is None and self.check_once: #game is over and we tried to at least once to test
            raise MyException(False)
        if game is None:
            self.count_bad_attempts += 1
            self.check_conditions(wanted_starting_time,wanted_diff)
        elif self.check_time(game,wanted_starting_time) and\
            self.check_diff(game,wanted_diff,wanted_starting_time):
            raise MyException(True)
        else:
            self.count_bad_attempts = 0
            self.scheduler.enter(DELAY,1,action=self.check_conditions,
                       argument=(wanted_starting_time,wanted_diff))
            self.scheduler.run()

    def check_time(self, game, wanted_starting_time,wanted_diff=0):
        curr_time_game = game.find('span').text
        if ":" in curr_time_game: # game didnt start
            print('game did not start')
            return False
        self.check_once = True
        if wanted_starting_time == 'Tiebreak': # only for tennis
            return self.check_tiebreak(game)
        assert curr_time_game in self.time_list.keys()
        return self.time_list[curr_time_game] >= self.time_list[wanted_starting_time]


    def check_diff(self,game,wanted_diff,wanted_starting_time=''):
        """
        Calculate the difference between scores of the 2 teams. Not all classes need to implement
        :param game: BeautifulSoup element contains the game's details
        :param wanted_diff: difference in score the user wishes to have
        :param wanted_starting_time: quarter the user want to start checking conditions
        :return: True if condition is meeting, False otherwise
        """
        return True

