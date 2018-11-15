from abstract import *



class Basketball(AbstractSport):
    def get_all_matches_by_league(self):
        """
        instead of querying the site twice (first leagues and then matches)
        :return: a dict mapping list of matches to their corrspondong league
        """
        self.limits = [0,20]
        self.time_list = {'Tip-off':0,'1Q':1,'2Q':2,'HT':3,'3Q':4,'4Q':5,'OT':6}
        soup = self.get_main_soup()
        league = ''
        games = {}
        # gamesList=soup.find_all(class_="row-group") # retrieve all the games
        divs = soup.find_all(class_=[re.compile("row row-tall"), "clear"])
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
            elif league != '' and div.find(class_="bas-ply") and\
                    (div.find("span").text not in finished_game or
                         div.find(class_='row-group live')): # todo change finished games
                game = div.find_all(class_="bas-ply")
                s = game[0].text + " Vs. " + game[1].text

                games[s] = div.get("data-id")
        if len(games):
            self.games_map[league] = games



    def check_diff(self, game, wanted_diff,wanted_starting_time =0):
        print(str(wanted_diff)+' points starting from '+wanted_starting_time)
        if wanted_starting_time in ['Tip-off','1Q']:
            return True
        scores = game.find_all(class_="sco3")
        score1 = int(scores[0].find('strong').text)
        score2 = int(scores[1].find('strong').text)
        return abs(score1-score2) <= wanted_diff