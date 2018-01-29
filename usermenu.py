# -*- coding: utf-8 -*-
from usermenutils import *
from multilang import *

class UserMenu:
    def __init__(self, chat_id, user_name, lang="rus"):
        self.db = BotDb(DB_PATH)
        self.menuReturn = MenuReturn(lang=lang)

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
            return self.menuReturn.r("Enter event name")
        elif data == "make_bet":
            self._set_state(STATE_SELECT_EVENT_FOR_BET)
            return self.menuReturn.r("Choose event for bet:", self._show_event_list(ALL_EVENTS))
        elif data == CMD_CLOSE_EVENT:
            ev_list = self.db.get_admin_events(self.info.user_id, EVENT_STATUS_CLOSED)
            if len(ev_list) > 0:
                self._set_state(STATE_SELECT_EVENT_FOR_CLOSE)
                return self.menuReturn.r("Choose event for close:", make_inline(ev_list, "name", "code"))
            return self.menuReturn.r("No Events for close!")
        elif data == CMD_PLAY_EVENT:
            ev_list = self.db.get_admin_events(self.info.user_id)
            if len(ev_list) > 0:
                self._set_state(STATE_SELECT_EVENT_FOR_PLAY)
                return self.menuReturn.r("Choose event for play:", make_inline(ev_list, "name", "code"))
            return self.menuReturn.r("No events for play")
        elif data == "info":
            self._set_state(STATE_ROOT)
            self.menutype = USER_MENU_TYPE_BASIC
            return self.menuReturn.r("your info in develop")
        elif data == "menu":
            self._set_state(STATE_ROOT)
            self.menutype = USER_MENU_TYPE_BASIC
            return self.menuReturn.r(self.tr("You are in main menu"))
        else:
            return self._proc_ev_for_bet(data)
        # ---------

    def _proc_ev_for_bet(self, data):
        self.info.event = self.db.load_event(data)
        if self.info.event:
            if self.info.event.status == EVENT_STATUS_OPEN:
                self._set_state(STATE_SELECT_VARIANT)
                return self.menuReturn.r("Choose variant", make_inline(self.info.event.variants, "name", "id"))
            else:
                return self.menuReturn.r("Event closed for bets!")
        else:
            return self.menuReturn.r("Wrong event code")

    # ---------
    def _proc_select_variant(self, data):
        self._set_state(STATE_MAKE_BET)
        self.info.selected = data # name of variant
        return self.menuReturn.r("Enter bet value:")


    #STATE_SELECT_WIN_VARIANT
    def _proc_select_win_variant(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Close event canceled")
        try:
            ret = self.db.play_event(self.info.event, int(data))
            winners_str = "/winner/ : /prize/\n"
            for w in ret.keys():
              winners_str += "%s : %f\n" % (w, ret[w])
            self._set_state(STATE_ROOT)
            users = self.db.get_event_user_list(self.info.event.id)
            ret_info = self.menuReturn.r("Event \"%s\" played:\n%s" % (self.info.event.name, winners_str), addr_list=users)
            return ret_info
        except:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Server problem #105")

    # ---------
    def _proc_make_bet(self, data):
        try:
            check_float = float(data)
            if type(check_float) != float:
                return self.menuReturn.r("Server problem #104")
            self.db.new_bet(self.info.user_id, self.info.selected, data)
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Bet is done")
        except TypeError:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Server problem #103")

    #STATE_SELECT_EVENT_FOR_CLOSE
    def _proc_close_ev(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Close event canceled")
        self.info.event = self.db.get_event(data)
        self.db.close_event(self.info.event)
        users = self.db.get_event_user_list(self.info.event.id)
        self._set_state(STATE_ROOT)
        ret = self.menuReturn.r("Event \"%s\" closed for bets (admin: %s)" % (self.info.event.name, self.info.user_name),
                         addr_list=users)
        return ret

    #STATE_SELECT_EVENT_FOR_PLAY
    def _proc_play_ev(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Play event canceled")
        self.info.event = self.db.get_event(data)
        self._set_state(STATE_SELECT_WIN_VARIANT)
        return self.menuReturn.r("Choose win variant", make_inline(self.info.event.variants, "name", "id"))

    # ---------
    def _proc_enter_event_name(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Create event canceled")
        else:
            self.info.event = BotEvent(name=data)
#            self.info.event.name = data
            self.info.event.variants = []
            self._set_state(STATE_ENTER_VARIANTS)
            return self.menuReturn.r("Enter variants for %s" % data)

    # ---------
    def _proc_enter_variant(self, data):
        if data == CMD_CANCEL:
            self._set_state(STATE_ROOT)
            return self.menuReturn.r("Create event canceled")
        elif data == CMD_STOP:
            if len(self.info.event.variants) < 2:
                return self.menuReturn.r("Enter at least 2 variants")
            self.info.event.admin_id = self.info.user_id
            self.info.event, result = self.db.add_new_event(self.info.event)
            self._set_state(STATE_ROOT)
            if result == "OK":
                return self.menuReturn.r("Event create compleate!\n",
                              [{"text": "Push to make a bet", "callback_data": self.info.event.code}],
                              ext=self.info.event.code)
            else:
                return self.menuReturn.r("Create event FAIL %s"%result)
        else:
            if data in self.info.event.variants:
                return self.menuReturn.r("Variant %s alredy exist!"% data)
            self.info.event.variants.append(data)
            return self.menuReturn.r("Ok! another variant?")


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
                return self.menuReturn.r("Server problem #101")
        except KeyError:
            print "No sach key %d" % self.state.info.state
            return self.menuReturn.r("Server problem #102")
