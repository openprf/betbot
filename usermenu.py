# -*- coding: utf-8 -*-
from usermenutils import *


class UserMenu:
    def __init__(self, chat_id, user_name):
        self.db = BotDb(DB_PATH)

        try:  # load user infj from cache
            f = open("cache/%s.user" % chat_id, "rb")
            self.info = pickle.load(f)
            f.close()
        except IOError as e:  # or create new user info
            self.info = UserInfo(self.db.user_id, chat_id=chat_id, user_name=user_name)

        #init menu functions
        self.state_funcs = {}
        self.init_state_funcs()

    def __del__(self):
        self.save()

    # ========================================
    # private

    def _set_state(self, state):
        self.info.state = state

    
    def _show_event_list(self, events = ADMIN_EVENTS):
        if events != ADMIN_EVENTS:
            event_list = self.db.get_user_events(self.info.user_id)
            return make_inline(event_list, "name", "code")
        else:
            event_list = self.db.get_admin_events(self.info.user_id)
            return make_inline(event_list, "name", "code")

    # ---------
    def _root_menu(self, data):
        if data == CMD_NEW_EVENT:
            self._set_state(STATE_ENTER_NEW_EVENT_NAME)
            return MenuReturn("Enter event name")
        elif data == "make_bet":
            self._set_state(STATE_SELECT_EVENT_FOR_BET)
            return MenuReturn("Choose event for bet:", self._show_event_list(ALL_EVENTS))
        elif data == CMD_CLOSE_EVENT:
            self._set_state(STATE_SELECT_EVENT_FOR_CLOSE)
            ev_list = self.db.get_admin_events(self.info.user_id, EVENT_STATUS_CLOSED)
            if len(ev_list) > 0:
                return MenuReturn("Choose event for close:", make_inline(ev_list, "name", "code"))
            return MenuReturn("No Events for close!")
        elif data == CMD_PLAY_EVENT:
            self._set_state(STATE_SELECT_EVENT_FOR_PLAY)
            ev_list = self.db.get_admin_events(self.info.user_id)
            if len(ev_list) > 0:
                return MenuReturn("Choose event for play:", make_inline(ev_list, "name", "code"))
            return MenuReturn("No events for play")
        elif data == "info":
            self._set_state(STATE_ROOT)
            self.menutype = USER_MENU_TYPE_BASIC
            return MenuReturn("your info in develop")
        elif data == "menu":
            self._set_state(STATE_ROOT)
            self.menutype = USER_MENU_TYPE_BASIC
            return MenuReturn("You are in main menu")
        else:
            return self._proc_ev_for_bet(data)
        # ---------

    def _proc_ev_for_bet(self, data):
        self.info.event = self.db.load_event(data)
        if self.info.event:
            if self.info.event.status == EVENT_STATUS_OPEN:
                self._set_state(STATE_SELECT_VARIANT)
                return MenuReturn("Choose variant", make_inline(self.info.event.variants, "name", "id"))
            else:
                return MenuReturn("Event closed for bets!")
        else:
            return MenuReturn("Wrong event code")

    # ---------
    def _proc_select_variant(self, data):
        self._set_state(STATE_MAKE_BET)
        self.info.selected = data # name of variant
        return MenuReturn("Enter bet value:")

    def _proc_select_win_variant(self, data):
        ret = self.db.play_event(self.info.event, int(data))
        winners_str = "/winner/ : /prize/\n"
        for w in ret.keys():
          winners_str += "%s : %f\n" % (w, ret[w])
        self._set_state(STATE_ROOT)
        return MenuReturn("Event \"%s\" played:\n%s" % (self.info.event.name, winners_str))

    # ---------
    def _proc_make_bet(self, data):
        try:
            check_float = float(data)
            if type(check_float) != float:
                return MenuReturn("Server problem #104")
            self.db.new_bet(self.info.user_id, self.info.selected, data)
            self._set_state(STATE_ROOT)
            return MenuReturn("Bet is done")
        except TypeError:
            self._set_state(STATE_ROOT)
            return MenuReturn("Server problem #103")

    # ---------
    def _proc_close_ev(self, data):
        self.info.event = self.db.get_event(data)
        self.db.close_event(self.info.event)
        self._set_state(STATE_ROOT)
        return MenuReturn("Event \"%s\" closed for bets (admin: %s)" % (self.info.event.name, self.info.user_name))

    # ---------
    def _proc_play_ev(self, data):
        self.info.event = self.db.get_event(data)
        self._set_state(STATE_SELECT_WIN_VARIANT)
        return MenuReturn("Choose win variant", make_inline(self.info.event.variants, "name", "id"))

    # ---------
    def _proc_enter_event_name(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return MenuReturn("Create event canceled")
        else:
            self.info.event = BotEvent(name=data)
#            self.info.event.name = data
            self.info.event.variants = []
            self._set_state(STATE_ENTER_VARIANTS)
            return MenuReturn("Enter variants for %s" % data)

    # ---------
    def _proc_enter_variant(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return MenuReturn("Create event canceled")
        elif data == CMD_STOP:
            if len(self.info.event.variants) < 2:
                return MenuReturn("Enter at least 2 variants")
            self.info.event.admin_id = self.info.user_id
            self.info.event, result = self.db.add_new_event(self.info.event)
            self._set_state(STATE_ROOT)
            if result == "OK":
                return MenuReturn("Event create compleate!\n",
                              [{"text": "Push to make a bet", "callback_data": self.info.event.code}],
                              ext=self.info.event.code)
            else:
                return MenuReturn("Create event FAIL %s"%result)
        else:
            if data in self.info.event.variants:
                return MenuReturn("Variant %s alredy exist!"% data)
            self.info.event.variants.append(data)
            return MenuReturn("Ok! another variant?")


    #--------
    def init_state_funcs(self):
        self.state_funcs[STATE_ROOT] = self._root_menu
        self.state_funcs[STATE_ENTER_NEW_EVENT_NAME] = self._proc_enter_event_name
        self.state_funcs[STATE_SELECT_VARIANT] = self._proc_select_variant
        self.state_funcs[STATE_MAKE_BET] = self._proc_make_bet
        self.state_funcs[STATE_ENTER_VARIANTS] = self._proc_enter_variant
        self.state_funcs[STATE_SELECT_EVENT_FOR_CLOSE] = self._proc_close_ev
        self.state_funcs[STATE_SELECT_EVENT_FOR_PLAY] = self._proc_play_ev
        self.state_funcs[STATE_SELECT_WIN_VARIANT] = self._proc_select_win_variant

    # ========================================
    # public

    def save(self):
        f = open("cache/%s.user" % self.info.chat_id, "wb")
        pickle.dump(self.info, f)
        f.close()

    def menutype(self):
        state = self.info.state
        if state == STATE_ROOT:
            return USER_MENU_ROOT
        if state == STATE_ENTER_VARIANTS:
            return USER_MENU_TYPE_STOP_ENTER_VARS
        return USER_MENU_CANCEL

    def do(self, data):
        try:
            func = self.state_funcs[self.info.state]
            try:
                return func(data)
            except AttributeError:
                self._set_state(STATE_ROOT)
                return MenuReturn("Server problem #101")
        except KeyError:
            print "No sach key %d" % self.state.info.state
            return MenuReturn("Server problem #102")
