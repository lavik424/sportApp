from abstract import *


class Tennis(AbstractSport):
    def get_all_matches_by_league(self):
        """
        instead of querying the site twice (first leagues and then matches)
        :return: a dict mapping list of matches to their corresponding tournament_name
        """
        self.time_list = {'Tiebreak':0,'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5}
        soup = self.get_main_soup()
        tournament_name = ''
        games = {}
        # gamesList=soup.find_all(class_="row-group") # retrieve all the games
        divs = soup.find_all(class_=[re.compile("row row-tall"), "clear"])
        for div in divs:
            if div.find(class_=[re.compile("left")]):
                tournament = div.find(class_=[re.compile("left")])
                temp_tournament = tournament.find('strong').text
                # temp_tournament += ' ' #TODO get second name correctly
                # second_name = tournament.find(class_=[re.compile("hidden-xxs")])
                # temp_tournament += second_name.get_text() if second_name else ''
                if temp_tournament == tournament_name:
                    continue
                else:
                    if tournament_name != '':
                        self.games_map[tournament_name] = games
                    tournament_name = temp_tournament
                    games = {}
            elif tournament_name != '' and div.find(class_="ten-ply") and\
                    (div.find("span").text not in finished_game or
                         div.find(class_='row-group live')): # todo change finished games
                game = div.find_all(class_="ten-ply")
                s = game[0].text + " Vs. " + game[1].text

                games[s] = (div.get("data-id"),div.find('span').text)
        if len(games):
            self.games_map[tournament_name] = games


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
        self.check_once = True
        if wanted_starting_time == 'Tiebreak': # only for tennis
            return self.check_tiebreak(game)


    def check_tiebreak(self,game):
        scores = game.find_all(class_=[re.compile("sco2")])
        scores1 = scores[0].find_all(class_=[re.compile("col")])
        scores2 = scores[1].find_all(class_=[re.compile("col")])
        for i in range(len(scores1)):
            if scores1[i].text == '' or scores2[i].text == '':
                return False
            if TIEBREAK_SCORE in scores1[i].text and TIEBREAK_SCORE in scores2[i].text:
                return True
        return False