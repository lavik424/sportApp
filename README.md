# sportApp

A sport application for pc, written in python using tkinter package.
Data was mined from  https://www.livescore.com using selenium package, chrome-driver and BeautifulSoup package.
I tried to use as many features as I could from tkinter and still keep them simple so you can learn from them.
 
Helpful sites for tkinter:
https://docs.python.org/3/library/tk.html
http://effbot.org/tkinterbook/

App purpose:
Are you tired of seeing defeats and one team crashing the other?
Are you like me want to see more dramatic moments as they happen?
If you do, maybe this app suits you.

It design to notify you when certain conditions are met.
For example you want to get a notification just if the game is tied getting into the 4 quarter,
or the tennis player are in a tiebreak.


How to use the app:
1. Choose 1 sport- either basketball, tennis or football (original football..).
2. Then you get a list of leagues/tournament to select from.
3. Double click on the desired league and a list of games will appear.
4. Double click on the desired match and then you will be presented with 2/1 options (basketball/tennis and football)
	+ Set a desired difference in the scores between the teams (between 0 to 20 points), relevant only for basketball.
	+ Set the desired time you wish to start checking the previous option.
5. If during the match the conditions you set were met, you will get a notifictaion, 
	otherwise you will be notified at the end of the match.
	
