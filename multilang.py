# -*- coding: utf-8 -*-
#Multilang support data


rus_data = {}

rus_data["Enter event name"] = "Введите название события"
rus_data["Choose event for bet:"] = "Выбирете событие для ставки"
rus_data["Choose event for close:"] = "Выбирите события для закрытия для ставок"
rus_data["Choose event for play:"] = "Введите событие для определения победителя"
rus_data["No events for play"] = "Нет событий для выбора победителя"
rus_data["You are in main menu"] = "Вы в главном меню"
rus_data["Choose variant"] = "Выберете вариант"
rus_data["Event closed for bets!"] = "Событие закрыто для ставок!"
rus_data["Wrong event code"] = "Неправильный код события"
rus_data["Enter bet value:"] = "Введите сумму ставки:"
rus_data["Close event canceled"] = "Закрытие события отменено"
rus_data["Bet is done"] = "Ставка сделана"
rus_data["Play event canceled"] = "Выбор победителя отменен"
rus_data["Choose win variant"] = "Выберете победивший вариант"
rus_data["Create event canceled"] = "Создания события отменено"
rus_data["Enter at least 2 variants"] = "Введите хотя бы 2 варианта"
rus_data["Ok! another variant?"] = "Хорошо, еще вариант?"


def tr_eng(str):
    return str


def tr_rus(str):
    try:
        ret_str = rus_data[str]
        return ret_str
    except KeyError:
        return str
