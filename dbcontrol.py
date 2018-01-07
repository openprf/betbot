# -*- coding: utf-8 -*-
import sqlite3

CREATE_DB_REQUEST_FILENAME = "res/botdb.init"

EVENT_STATUS_OPEN = 0
EVENT_STATUS_CLOSED = 1
EVENT_STATUS_PLAYED = 2
EVENT_STATUS_NOTDEFINED = -1


class BotEvent:
  def __init__(self, id=0, code="", name="", admin_id=0, status=EVENT_STATUS_NOTDEFINED):
    self.id = id
    self.code = code
    self.name = name
    self.admin_id = admin_id
    self.status = status
    self.variants = []


  def __retr__(self):
    print "Event %s (code: %s)" % (self.name, self.code)
#=============================

class BotDb:
  def __init__(self, fname):
    self.conn = sqlite3.connect(fname)
    self.cursor = self.conn.cursor()


  def __del__(self):
    self.conn.close()
    print "DB closed"


  def __retr__(self):
    print self.conn

#------------------------------
#private:

  def _read(self, req, args):
    self.cursor.execute(req, args)
    return self.cursor.fetchall()


  def _write(self, req, args):
    self.cursor.execute(req, args)
    self.cursor.fetchall()
    self.conn.commit()


  def _add_user(self, chat_id, user_name):
    self._write("INSERT OR REPLACE INTO users (chat_id, name) VALUES( :chat_id, :user_name)", {"chat_id": chat_id, "user_name":user_name})
    return self.cursor.lastrowid
    
#-------------------------------
#public:
  # ===================================================================
  # new interface
  def create_tables(self):
    reqfile = open(CREATE_DB_REQUEST_FILENAME, 'r')
    lines = reqfile.readlines()
    reqfile.close()
    for line in lines:
      print line
      self.cursor.execute(line)
    self.cursor.fetchall()
    self.conn.commit()


  def get_user_id(self, chat_id, user_name):
    res = self._read("SELECT id, name, state FROM users WHERE chat_id = :chat_id", {"chat_id":chat_id})
    user_id = 0
    user_state = 0
    if res:
      user_id = res[0][0]
      user_state = res[0][2]
      if res[0][1] != user_name:
	    print "user_name changed from ", res[0][1], " to ", user_name
	    self._write("UPDATE users SET name = :user_name WHERE chat_id = :chat_id", {"user_name":user_name, "chat_id":chat_id})
    else:
      print "User not found! add new user: ", user_name
      user_id = self._add_user(chat_id, user_name)
    return user_id, user_state


  def add_event(self, admin_id, event_name):
    self._write("INSERT OR REPLACE INTO events (name , admin_id, status) VALUES(:name, :admin_id, 0)", {"name": event_name, "admin_id":admin_id})
    event_id = self.cursor.lastrowid 
    name_hash = hash(event_name)
    code = "%X%X" % (event_id, name_hash)
    print "added code: ", code
    self._write("UPDATE events SET code = :code WHERE id = :id", {"code":code, "id":event_id})
    return BotEvent(event_id, code, event_name, admin_id, 0)


  def add_variant(self, event_id, variant_name):
    self._write("INSERT OR REPLACE INTO variants (event_id, name) VALUES(:event_id, :name)", {"event_id":event_id, "name": variant_name})


  def get_event(self, event_code):
    res = self._read("SELECT id ,code, name, admin_id, status FROM events WHERE code = :code", {"code":event_code})
    if res:
      event = BotEvent(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
      variants = self._read("SELECT id, name FROM variants WHERE event_id = :event_id", {"event_id":event.id})
      for v in variants:
	event.variants.append({"id":v[0], "name":v[1]})
      return event


  def load_variants(self, event_id):
    res = self._read("SELECT id, name FROM variants WHERE event_id = :event_id", {"event_id":event_id})
    return res


  def add_bet(self, user_id, variant_id, value):
    self._write("INSERT OR REPLACE INTO bets (user_id, variant_id, value) VALUES(:user_id, :var_id, :bet_val)", {"user_id": user_id, "var_id":variant_id, "bet_val":value})


  def close_event(self, event):
    self._write("UPDATE events SET status = 1 WHERE id = :id", {"id":event.id})


  def play_event(self, event, win_var_id):
    self._write("UPDATE events SET status = 2 WHERE id = :id", {"id":event.id})
    req = """SELECT bets.[user_id], bets.[value], bets.[variant_id], users.[name] FROM bets, users 
    WHERE bets.[user_id] = users.[id] AND bets.[variant_id] IN (SELECT id FROM variants WHERE event_id = :event_id)"""
    res = self._read(req, {"event_id":event.id})
    prize = 0.0
    win_bets = 0.0
    wins = {}
    for r in res:
      prize += r[1]
      if r[2] == win_var_id:
	win_bets += r[1]
	if r[3] in wins:
	  wins[r[3]] += r[1]
	else:
	  wins[r[3]] = r[1]	
    
#    print "prize %f, win bets %f" % (prize, win_bets)
#    print wins
    
    for w in wins.keys():
      wins[w] = prize*wins[w]/win_bets
      
    return wins


  def get_user_events(self, user_id):
    req = "SELECT name, code FROM events WHERE id IN (SELECT event_id FROM variants WHERE id IN (SELECT variant_id FROM bets WHERE user_id = :user_id))"
    res = self._read(req,{"user_id":user_id})
    events = []
    for r in res:
      events.append({"name":r[0], "code":r[1]})
    return events


  def get_admin_events(self, user_id):
    req = "SELECT name, code FROM events WHERE admin_id = :user_id"
    res = self._read(req,{"user_id":user_id})
    events = []
    for r in res:
      events.append({"name":r[0], "code":r[1]})
    return events


  def get_user_bets(self, user_id):
    req = """ SELECT events.[name], variants.[name], bets.[value] FROM events, variants, bets WHERE 
    bets.[user_id] = :user_id AND bets.[variant_id] = variants.[id] AND variants.[event_id] = events.[id] 
    GROUP BY bets.[id]"""
    res = self._read(req,{"user_id":user_id})
    bets = []
    for r in res:
      bets.append({"event":r[0], "variant":r[1], "value":r[2]})
    return bets


  def update_user_state(self, user_id, state):
    self._write("UPDATE users SET state = :state WHERE id = :user_id", {"user_id": user_id, "state": state})


  def user_bets_and_events_count(self, user_id):
    bets = self.get_user_bets(user_id)
    events = self.get_user_events(user_id)
    return len(bets), len(events)


  def clear_event(event):
    pass


#===================================================================
# new interface
  def user_id(self, chat_id, user_name):
      res = self._read("SELECT id, name, state FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
      if res:
        user_id = res[0][0]
        if res[0][1] != user_name:
          print "user_name changed from ", res[0][1], " to ", user_name
          self._write("UPDATE users SET name = :user_name WHERE chat_id = :chat_id",
                      {"user_name": user_name, "chat_id": chat_id})
        return user_id
      else:
        print "User not found! add new user: ", user_name
        return self._add_user(chat_id, user_name)


  def add_new_event(self, new_event):
#    self._write("BERIN TRANSACTION")
    self._write("INSERT INTO events (name , admin_id, status) VALUES(:name, :admin_id, 0)",
                {"name": new_event.name, "admin_id": new_event.admin_id})
    new_event.id = self.cursor.lastrowid
    name_hash = hash(new_event.name)
    new_event.code = "%X%X" % (new_event.id, name_hash)
    print "added code: ", new_event.code
    self._write("UPDATE events SET code = :code WHERE id = :id", {"code": new_event.code , "id": new_event.id})
    for vr in new_event.variants:
      self._write("INSERT INTO variants (event_id, name) VALUES(:event_id, :name)",
                  {"event_id": new_event.id, "name": vr})
#    self._write("COMMIT TRANSACTION")
    return new_event, "OK"

  def load_event(self, event_code):
    res = self._read("SELECT id ,code, name, admin_id, status FROM events WHERE code = :code", {"code":event_code})
    if res:
      event = BotEvent(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
      variants = self._read("SELECT id, name FROM variants WHERE event_id = :event_id", {"event_id":event.id})
      for v in variants:
	event.variants.append({"id":v[0], "name":v[1]})
      return event

  def new_bet(self, user_id, variant_id, value):
    #ret = self._read("SELECT id FROM variants WHERE id = :variant_id ", {"variant_id": variant_id})
    #variant_id = ret[0][0]
    self._write("INSERT OR REPLACE INTO bets (user_id, variant_id, value) VALUES(:user_id, :var_id, :bet_val)", {"user_id": user_id, "var_id":variant_id, "bet_val":value})