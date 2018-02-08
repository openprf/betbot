# -*- coding: utf-8 -*-
#main bot logic

import config #This file contains telegram bot token. Get your own token from @botfather!
import telebot
from telebot import types
from usermenu import *
from dbcontrol import *


bot = telebot.TeleBot(config.token)

log.info("OK, we are start!")

#TODO: initial setting
def bot_init():
    pass

def get_user(chat_id, username):
    user = UserMenu(chat_id, username)
    return user

def del_user(user, chat_id):
    user.save()


#get keybord from type
def make_kayboard(type = USER_MENU_ROOT):
    keyboard = types.ReplyKeyboardMarkup()

    if type == USER_MENU_TYPE_STOP_ENTER_VARS:
        keyboard.row(CMD_CANCEL, CMD_STOP)
    elif type == USER_MENU_CANCEL:
        keyboard.row(CMD_CANCEL)
    elif type == USER_MENU_ROOT:
        keyboard.row(CMD_HELP, CMD_MY_BETS)
        keyboard.row(CMD_NEW_EVENT, CMD_CLOSE_EVENT, CMD_PLAY_EVENT)

    return keyboard


#Send message to users
def send(user, info):
    log.debug("sending to user %s" % user.info.user_name)
    #process multicast messages
    if len(info.addrs) > 0:
        log.debug("multicat (addr count %d)" % len(info.addrs))
        for chat_id in info.addrs:
            bot.send_message(chat_id, info.text)
    else:
        log.debug("unicast")
        key_board = make_kayboard(user.menutype())
        #process unicast messages
        if len(info.inline) == 0:
            key_board = make_kayboard(user.menutype())
            bot.send_message(user.info.chat_id, info.text, reply_markup=key_board)
        else:
            log.debug("inline menu len %d" % len(info.inline))
            inline_kbd = types.InlineKeyboardMarkup()
            for btn in info.inline:
                btn = types.InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
                inline_kbd.add(btn)
            bot.send_message(user.info.chat_id, info.text, reply_markup=inline_kbd)

        if len(info.ext) > 0:
            bot.send_message(user.info.chat_id, info.ext, reply_markup=key_board)


# @bot.message_handler (commands=['/help'])
# def helpHandler(message):
#     f = open("res/help.txt", "r")
#     helptext = f.read()
#     f.close()
#     bot.send_message(message.chat.id, helptext, reply_markup=make_kayboard())


@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    try:
        if call.message:
            message = call.message
            user = get_user(message.chat.id, message.from_user.username)
            info = user.do(call.data)

            send(user, info)

            # if len(info.inline) > 0:
            #     inline_kbd = types.InlineKeyboardMarkup()
            #     for btn in info.inline:
            #         btn = types.InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
            #         inline_kbd.add(btn)
            #     bot.send_message(message.chat.id, info.text, reply_markup=inline_kbd)
            # bot.send_message(message.chat.id, info.text, reply_markup=make_kayboard(user.menutype()))

            del_user(user, message.chat.id)

        elif call.inline_message_id:
            print call.inline_message_id
    except:
        log.error("Promlem with callbackHandler")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_msg(message):
    try:
        user = get_user(message.chat.id, message.from_user.username)
        info = user.do(message.text)

        send(user, info)

        # key_board = make_kayboard(user.menutype())
        # bot.send_message(message.chat.id, info.text, reply_markup=key_board)
        #
        # if len(info.inline) > 0:
        #     inline_kbd = types.InlineKeyboardMarkup()
        #     for btn in info.inline:
        #         btn = types.InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
        #         inline_kbd.add(btn)
        #     bot.send_message(message.chat.id, info.text, reply_markup=inline_kbd)
        #
        # if len(info.ext) > 0:
        #     bot.send_message(message.chat.id, info.ext, reply_markup=key_board)

        del_user(user, message.chat.id)

        #отправка сообщений вместе с клавиатурой
        #bot.send_message(message.chat.id, message.text, reply_markup=kb1)
    except AttributeError as e:
        log.error("Promlem with process_msg (error {0})".format(e))

if __name__ == '__main__':
    bot_init()
    bot.polling(none_stop=True)