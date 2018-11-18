from abstract import *


class Football(AbstractSport):
    def get_all_matches_by_league(self):
        """
        instead of querying the site twice (first leagues and then matches)
        :return: a dict mapping list of matches to their corrspondong league
        """
        self.limits = [0,3]
        self.time_list = range(SOCCER_GAME_LENGTH)
        soup = self.get_main_soup()
        league = ''
        games = {}
        # gamesList=soup.find_all(class_="row-group") # retrieve all the games
        divs = soup.find_all(attrs= {'data-type':['stg','evt']})
        for div in divs:
            if div.find(class_=[re.compile("left")]):
                temp_league = div.find(class_=[re.compile("left")]).find('strong').get_text()
                if temp_league == league:
                    continue
                else:
                    if league != '':
                        self.games_map[league] = games
                    league = temp_league
                    games = {}
            elif league != '' and div.get('data-type')=='evt'  and\
                    (div.find("span").text not in finished_game or
                         div.find(class_='row-group live')): # todo change finished games

                s = div.find(class_='ply tright name').text + " Vs. " +\
                    div.find(class_='ply name').text

                games[s] = (div.get("data-id"),div.find('span').text)
        if len(games):
            self.games_map[league] = games


    def check_time(self, game, wanted_starting_time,wanted_diff=0):
        """

        :param game:
        :param wanted_starting_time:
        :param wanted_diff:
        :return:
        """
        curr_time_game = game.find('span').text
        if ":" in curr_time_game: # game didnt start
            print('game did not start')
            return False
        if curr_time_game == 'HT':
            curr_time_game = 45
        else:
            curr_time_game = self.extract_minute(curr_time_game)
        self.check_once = True
        assert curr_time_game >= 0 and curr_time_game <= 90
        return curr_time_game >= int(wanted_starting_time)

    def extract_minute(self,min_text):
        res = ''
        for c in min_text:
            if str.isnumeric(c):
                res += c
            else:
                return int(res)
        return int(res)


    def get_time_list(self):
        return self.time_list


    def check_diff(self,game,wanted_diff,wanted_starting_time=''):
        """
        Calculate the difference between scores of the 2 teams. Not all classes need to implement
        :param game: BeautifulSoup element contains the game's details
        :param wanted_diff: difference in score the user wishes to have
        :param wanted_starting_time: quarter the user want to start checking conditions
        :return: True if condition is meeting, False otherwise
        """
        if wanted_starting_time == '0':
            return True
        score1 = int(game.find(class_='hom').text)
        score2 = int(game.find(class_='awy').text)
        return abs(score1-score2) <= wanted_diff