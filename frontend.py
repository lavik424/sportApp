#===============================================================================
# Imports
#===============================================================================
from tkinter import *
from tkinter import ttk
from basketball import Basketball
from tennis import Tennis
from football import Football
from winsound import PlaySound
from winsound import SND_FILENAME
from utils import MyException, CONNECTION_ERROR, SUCCESS, FAILURE
from tkinter import messagebox
import sys, time, six


sports = {'foot': 'Football', 'tennis': 'Tennis', 'basket': 'Basketball'}
sport = None

def start_gui():
    root = Tk()

    def handle_exception(*args):
        if sys.exc_info()[0] != MyException:
            t,v,tb = sys.exc_info()
            raise six.reraise(t,v,tb)
            return
        ans = sys.exc_info()[1].res
        if ans == CONNECTION_ERROR:
            messagebox.showerror('unable to proceed','Please check your internet connection')
            return
        last_statement(conditions_ans=ans)

    def controlled_exit():
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            root.destroy()

    def restart():
        if messagebox.askokcancel("Restart", "Restart captain?"):
            root.destroy()
            start_gui()

    def sport_command(*args):
        """
        After choosing 1 sport retrieve a leagues list
        :param args:
        :return:
        """
        b1.state(['disabled'])
        if sportName.get() == '':
            sentlbl.config(text="Please choose 1 sport from above")
            b1.state(['!disabled'])
            return
        sentlbl.config(text="Please wait..")
        sentlbl.update_idletasks()
        global sport
        if sportName.get() == 'tennis':
            sport = Tennis(sportName.get())
        elif sportName.get() == 'basket':
            sport = Basketball(sportName.get())
        else:
            sport = Football(sportName.get())
        lst = sport.get_leagues()
        leagueList.set(lst)
        for i in range(0, len(lst), 2):
            list1.itemconfigure(i, background='#f0f0ff')
        sentlbl.config(text='')
        list1.bind('<Double-1>', show_games)


    def show_games(*args):
        """
        After choosing 1 league, retrieve list of games in desired league
        :param args: from below
        :return: massage and list of games by corresponding league
        """
        gameList.set('')
        notification.grid_forget()
        idxs = list1.curselection()[0]
        temp = leagueList.get().split(sep=',')
        name = ''.join(filter(str.isalpha,temp[idxs]))
        lst = sport.get_games_by_league(name)
        if len(lst)==0:
            sentlbl.config(text='No games were found')
            return
        gameList.set(lst)
        for i in range(0, len(lst), 2):
            list2.itemconfigure(i, background='#90EE90')
        sentlbl.config(text='Please select one game to get notification')
        list2.bind('<Double-1>', select_match)


    def already_selected_league(*args):
        sentlbl.config(text='You have already selected a league..')

    def already_selected_match(*args):
        sentlbl.config(text='You have already selected a match.. you can restart')


    def select_match(*args):
        """
        After choosing 1 match, calls for set_notification_frame()
        :param args:
        :return:
        """
        idxs = list2.curselection()[0]
        temp = gameList.get().split(sep=',')
        sport.game_name = temp[idxs]
        game_name = ''.join(filter(str.isalpha,temp[idxs]))
        if sport.game_time == '': # not first time
            sport.set_game_id(game_name)
            set_notification_frame()
        else:
            sport.set_game_id(game_name)
            set_notification_frame2()

        sentlbl.config(text='')



    def set_notification_frame(*args):
        """
        Draw the notification frame, after game choosing
        :param args:
        :return:
        """
        notification.grid(column=0, row=5, columnspan=5, sticky=(N, W, E, S))
        line = sport.game_name
        if ':' in sport.game_time:
            line += ' is starting at ' + sport.game_time
        else:
            line += ' is currently at ' + sport.game_time

        mes_game_details.config(text=line)
        if sport.limits is not None:
            diff_spinbox = ttk.Spinbox(diff, from_=sport.limits[0],
                                       to=sport.limits[1],textvariable=diffVar)
            diff_spinbox.set(sport.limits[0])
            diff_spinbox.grid(row=0, column=0)
        if sport.time_list is not None:
            time_list = sport.get_time_list()
            timeToCheck.set(time_list[0])
            if sport.game_id is not '':
                time_mb = ttk.Menubutton(checking_time, textvariable=timeToCheck)
                time_mb.menu = Menu(time_mb, tearoff=0)
                time_mb['menu'] = time_mb.menu
                for t in time_list:
                    time_mb.menu.add_radiobutton(label=t, variable=timeToCheck)
                time_mb.grid()

    def set_notification_frame2(*args):
        notification.grid_forget()
        notification.grid(column=0, row=5, columnspan=5, sticky=(N, W, E, S))
        line = sport.game_name
        if ':' in sport.game_time:
            line += ' is starting at ' + sport.game_time
        else:
            line += ' is currently at ' + sport.game_time
        mes_game_details.config(text=line)


    def start_query(*args):
        """
        After user chooses the conditions, start checking if they were met
        :param args:
        :return:
        """
        get_noti_button.configure(command=already_selected_match)
        list1.bind('<Double-1>',already_selected_match)
        list2.bind('<Double-1>', already_selected_match)
        line = 'You have selected to get notifications for ' + sport.game_name
        mes_notifi_up.config(text=line)
        mes_notifi_down.config(text='You will receive a message when the conditions met')
        root.update_idletasks()
        sport.query_game(timeToCheck.get(),diffVar.get())




    def last_statement(conditions_ans,*args):
        """
        Draw last message to user,
        :param conditions_ans: True if conditions were met, False otherwise
        :param args:
        :return:
        """
        line = 'In ' + sport.game_name
        line += ' a difference of ' + str(diffVar.get()) + ' points starting from ' + timeToCheck.get()
        if conditions_ans == SUCCESS:
            print('Conditions were met')
            line += ' was achieved!!'
            PlaySound('C:/Windows/media/Alarm01.wav', SND_FILENAME)
            message = 'Its time to start watching!! ' + time.ctime()
            messagebox.showinfo(message=message)
        else:
            print('Game ended and Conditions were not met')
            line += ' was not achieved..'
            messagebox.showinfo(message='Bummer!!')
        mes_notifi_up.config(text=line)
        mes_notifi_down.destroy()


    #===============================================================================
    # Vars
    #===============================================================================
    sportName = StringVar()
    leagueList = StringVar()
    gameList = StringVar()
    diffVar = IntVar()
    diffVar.set(0)
    timeToCheck = StringVar()



    root.title("Be there when it goes down")

    c = ttk.Frame(root, padding=(5, 5, 12, 0))
    c['borderwidth'] = 20
    c['relief'] = 'groove'
    c.grid(column=0, row=0, sticky=(N, W, E, S))
    #===============================================================================
    # Frame
    #===============================================================================
    sport_frame = ttk.LabelFrame(c,text='Sport')
    sport_frame.grid(row=0,column=0,sticky=NW)
    games_frame = ttk.LabelFrame(c,text='Games')
    games_frame.grid(row=0,column=1,rowspan=2,sticky=(N, W, E, S))
    leagues_frame = ttk.LabelFrame(c,text='Leagues/Tournaments')
    leagues_frame.grid(row=1,column=0,sticky=NW)


    notification = ttk.LabelFrame(c,text='Notification Options')
    diff = ttk.LabelFrame(notification,text='Difference',padding=[5,5])
    diff.grid(column=0,row=1,sticky=W)
    checking_time = ttk.LabelFrame(notification,text='Start checking in')
    checking_time.grid(column=1,row=1,sticky=(N, W, E, S))


    #===============================================================================
    # Label/Message
    #===============================================================================

    sentlbl = ttk.Label(sport_frame, anchor='center')
    sentlbl.grid(column=0, row=5, columnspan=2, sticky=S, pady=5, padx=5)
    mes_notifi_up = Message(notification,width=600)
    mes_notifi_up.grid(column=0, row=4, columnspan=5, sticky=N)
    mes_notifi_down = Label(notification)
    mes_notifi_down.grid(column=0, row=5, columnspan=5, sticky=N)
    mes_game_details = Message(notification,width=600)
    mes_game_details.grid(column=0, row=0, columnspan=5, sticky=N)

    #===============================================================================
    # Radiobutton
    #===============================================================================
    r1 = ttk.Radiobutton(sport_frame, text=sports['basket'], variable=sportName,value='basket')
    r2 = ttk.Radiobutton(sport_frame, text=sports['foot'], variable=sportName,value='foot')
    r3 = ttk.Radiobutton(sport_frame, text=sports['tennis'], variable=sportName,value='tennis')

    r1.grid(column=1, row=1, sticky=W, padx=20)
    r2.grid(column=1, row=2, sticky=W, padx=20)
    r3.grid(column=1, row=3, sticky=W, padx=20)


    #===============================================================================
    # Buttons
    #===============================================================================

    b1 = ttk.Button(sport_frame,text='Choose sport',width=20,
                    command=sport_command)
    b1.grid(column=1, row=4, sticky=W, padx=20)
    restart_button = ttk.Button(c,text='Restart',width=20,
                    command=restart)
    restart_button.grid(column=0, row=10,columnspan=2,  sticky=N)

    get_noti_button = ttk.Button(notification, text='Get notifications', width=20,
                    command=start_query)
    get_noti_button.grid(column=2, row=1, sticky=W, padx=20)

    #===============================================================================
    # ListBox
    #===============================================================================
    ### ListBox - Leagues###
    list1=Listbox(leagues_frame, height=6, width=25, listvariable=leagueList)
    list1.grid(row=7,column=1,sticky=(N, W, E, S))
    sb1=Scrollbar(leagues_frame)
    sb1.grid(row=7,column=0,rowspan=6,sticky=W)
    list1.configure(yscrollcommand=sb1.set)
    sb1.configure(command=list1.yview)

    ### ListBox - Games###

    list2=Listbox(games_frame, height=15, width=50, listvariable=gameList)
    list2.grid(row=1,column=3,rowspan=10,columnspan=2,sticky=(N, W, E, S))
    sb2=Scrollbar(games_frame)
    sb2.grid(row=1,column=2,rowspan=10,sticky=(N, W, E, S))
    list2.configure(yscrollcommand=sb2.set)
    sb2.configure(command=list2.yview)


    root.protocol("WM_DELETE_WINDOW", controlled_exit)



    Tk.report_callback_exception = handle_exception



    root.mainloop()



start_gui()