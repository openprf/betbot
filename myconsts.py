DB_PATH = "res/botdb.sqlite"

#user menu states
STATE_ROOT = 0
STATE_SELECT_VARIANT = 1
STATE_MAKE_BET = 2
STATE_ENTER_NEW_EVENT_NAME = 3
STATE_ENTER_VARIANTS = 4
#STATE_MAKE_BET_QUESTION = 5 #inline button
STATE_SELECT_EVENT_FOR_CLOSE = 6
STATE_SELECT_EVENT_FOR_PLAY = 7
STATE_SELECT_WIN_VARIANT = 8
STATE_SELECT_EVENT_FOR_BET = 9 #not use now

#types of keybord
USER_MENU_TYPE_BASIC = 0 #user haven't bets or own events
USER_MENU_TYPE_BETS = 1 #user haven't own events but have own events
USER_MENU_TYPE_BETS_AND_EVENTS = 3 #user have both own events and bets
USER_MENU_TYPE_TO_ROOT = 4

USER_MENU_TYPE_STOP_ENTER_VARS = 5
USER_MENU_CANCEL = 6
USER_MENU_ROOT = 7

#unicats send addr
EVENT_ADDR_UNICAST = -1

#event types
ALL_EVENTS = 0
ADMIN_EVENTS = 1

#commands
CMD_CANCEL = "/cancel"
CMD_NEW_EVENT = "/newevent"
CMD_CLOSE_EVENT = "/closeevent"
CMD_PLAY_EVENT = "/playevent"
CMD_MY_BETS = "/mybets"
CMD_STOP = "/stop"
CMD_HELP = "/help"
CMD_ABOUT = "/about"