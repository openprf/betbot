# -*- coding: utf-8 -*-
import logging
import logging.handlers

#init log subsystem
log = logging.getLogger('betbot')
handler = logging.FileHandler('betbot.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)