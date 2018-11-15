from abstract import *


class Tennis(AbstractSport):
    def get_all_matches_by_league(self):
        """
        instead of querying the site twice (first leagues and then matches)
        :return: a dict mapping list of matches to their corresponding tournament_name
        """
        self.time_list = {'S1': 0, 'S2': 1, 'S3': 2, 'S4': 3, 'S5': 4}  # TODO add tiebreak
        soup = self.get_main_soup()
        tournament_name = ''
        games = {}
        # gamesList=soup.find_all(class_="row-group") # retrieve all the games
        divs = soup.find_all(class_=[re.compile("row row-tall"), "clear"])
        for div in divs:
            if div.find(class_=[re.compile("left")]):
                tournament = div.find(class_=[re.compile("left")])
                temp_tournament = tournament.find('strong').get_text()
                temp_tournament += ' '
                temp_tournament += tournament.find(class_=[re.compile("hidden-xxs")]).get_text()
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

                games[s] = div.get("data-id")
        if len(games):
            self.games_map[tournament_name] = games


    def check_tiebreak(self,game):
        pass