from myconsts import *
from dbcontrol import *
import pickle

def make_inline(inlist, text, callback_data):
    inline = []
    for item in inlist:
        inline.append({"text": item[text], "callback_data": item[callback_data]})
    return inline


class MenuReturn:
    def __init__(self, text, inline=[], event_addr=EVENT_ADDR_UNICAST, ext="", addr_list=[]):
        #print "return text: ", text
        self.text= text
        self.inline = inline
        self.event_addr = event_addr
        self.ext = ext
        self.addrs = addr_list
        if len(self.inline) > 0 and self.ext == "":
            self.ext = "---"



    def txt(self, num):
      return self.inline[num]["text"]


    def call_back(self, num):
      return self.inline[num]["callback_data"]


class UserInfo:
    def __init__(self, getuser, user_name="", chat_id=0):
        self.user_id = getuser(chat_id, user_name)
        self.user_name = user_name
        self.event = BotEvent()
        self.state = STATE_ROOT
        self.chat_id = chat_id
        self.selected = ""

    def __del__(self):
        pass