# -*- coding: utf-8 -*-
######################################libs######################################

import sys
import os
from telegram.ext import *
from telegram import *
from functools import wraps
import time
from datetime import datetime
from pylab import figure, axes, pie, title, show
import matplotlib.pyplot as plt
import math
import random
import requests
import json
import numpy as np
from functools import wraps
import sqlite3
#sys.path.insert(0, '/home/plombir/.local/lib/python3.6/site-packages')
######################################TOKEN#####################################
updater = Updater(token='898799553:AAG5nLoXPb-nDAdI6OU_AVOPlXt5j7387xM')
dispatcher = updater.dispatcher
j = updater.job_queue
conn = sqlite3.connect('bot.db')
c = conn.cursor()
# DELETE TABLE
#c.execute("DROP TABLE subs")
# Create table
c.execute("CREATE TABLE IF NOT EXISTS subs (id char not null primary key, parent_id char, balance int, tokens int, referals int, status int)")
sql = "SELECT * FROM subs"
c.execute(sql)
print(c.fetchall()) # or use fetchone()
# Insert a row of data
conn.commit()
#c.execute("INSERT INTO subs VALUES (?,0)", ['371641854'])
#conn.commit()
# Save (commit) the changes
conn.close()
price=200
temp=0
def ups(bot,update):
    global price, temp
    price=round(1.01*price,1)
    api_access_token = '4d592b507c46b5c38c95fd39a47b6998' # токен можно получить здесь https://qiwi.com/api
    my_login = '+79059152103' # номер QIWI Кошелька в формате +79991112233
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows':10,'startDate': '2018-10-01T00:00:00+03:00','endDate': '2018-10-31T11:44:15+03:00'}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/'+my_login+'/payments?rows=10')
    #print(h.text)
    dic=json.loads(h.text)

    comm=str(dic['data'][0]['comment'])
    summ=float(dic['data'][0]['sum']['amount'])
    #print("Сумма платежа: "+str(dic['data'][0]['sum']['amount']))
    #print("\nТип платежа: "+str(dic['data'][0]['type']))
    #print("\nОтправитель: "+str(dic['data'][0]['account']))
    #print("\nКомментарий: "+str(dic['data'][0]['comment']))
    if temp!=comm:
        temp=comm
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()
        c.execute("UPDATE subs SET balance=balance+? WHERE id=?",[summ,comm])
        conn.commit()
        conn.close()
    #if(comm==user):
        #balance=balance+summ
        #bot.answer_callback_query(callback_query_id=query.id, show_alert=False, text=("На ваш счет зачислено "+str(summ)+ "рублей"))
    #else:
        #bot.answer_callback_query(callback_query_id=query.id, show_alert=False, text=("Переводов не обнаружено"))
#IF Not Exists (select * from subs where id=?)
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
job_minute = j.run_repeating(ups, interval=2, first=0)
message_token=0
message_balance=0
###################################STARTCOMMAND#################################
def startCommand(bot, update, args=None):
    bot.send_chat_action(chat_id=update.message.from_user.id, action=ChatAction.TYPING)
    user = str(update.message.from_user.id)
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM subs WHERE id=?",[user])
    a=c.fetchall()
    if not a:
        c.execute("INSERT INTO subs VALUES (?,'000000000',10000,0,0,1)", [user])
        if args:
            c.execute("UPDATE subs SET referals=referals+1 WHERE id=?",[args[0]])
            c.execute("UPDATE subs SET parent_id=? WHERE id=?",[args[0],user])
            c.execute("SELECT referals FROM subs WHERE id=?",[args[0]])
            [b],=c.fetchall()
            c.execute("SELECT status FROM subs WHERE id=?",[args[0]])
            [e],=c.fetchall()
            if b>0 and e<2:
                c.execute("UPDATE subs SET status=2 WHERE id=?",[args[0]])
            if b>=10 and e<3:
                c.execute("UPDATE subs SET status=3 WHERE id=?",[args[0]])
            if b>=25 and e<4:
                c.execute("UPDATE subs SET status=4 WHERE id=?",[args[0]])
            if b>=50 and e<5:
                c.execute("UPDATE subs SET status=5 WHERE id=?",[args[0]])
    conn.commit()
    sql = "SELECT * FROM subs"
    c.execute(sql)
    print(c.fetchall())
    conn.close()
    keyboard = [['♟TonGram', '💰Balance'],
                   ['📜About', '👥Company']]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    bot.send_message(chat_id=user, text="Здравствуй, *инвестор*👤 \n\nЯ - новый бот для обмена криптовалюты *TON*💎\n\nВсе очень просто: *вы покупаете токены, а я слежу за их курсом и возвращаю с процентом*📊", reply_markup=reply_markup,parse_mode=ParseMode.MARKDOWN)
###################################MESSAGECOMMAND###############################
def textMessage(bot,update):
    global price, message_token, message_balance
    bot.send_chat_action(chat_id=update.message.from_user.id, action=ChatAction.TYPING)
    user = str(update.message.from_user.id)
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM subs WHERE id=?",[user])
    [balance],=c.fetchall()
    c.execute("SELECT tokens FROM subs WHERE id=?",[user])
    [tokens],=c.fetchall()
    c.execute("SELECT status FROM subs WHERE id=?",[user])
    [status],=c.fetchall()
    c.execute("SELECT referals FROM subs WHERE id=?",[user])
    [referals],=c.fetchall()
    c.execute("SELECT parent_id FROM subs WHERE id=?",[user])
    [parent_id],=c.fetchall()
    conn.commit()
    conn.close()

    ticks = {1: 'Клерк', 2: 'Партнер', 3: 'Менеджер', 4: 'Управленец', 5: 'Директор'}
    tick = ticks.get(status)

    command=update.message.text
    answer=""
    # Main
    keyboard = [['♟TonGram', '💰Balance'],
                   ['📜About', '👥Company']]
    if command=="♟TonGram":
        answer+=("Токены: *{}*".format(tokens))
        answer+=("\nКурс: *{} руб*".format(price))
        keyboard = [['🔹Купить', '🔻Продать'],
                       ['🔙Меню']]
    elif command=="🔹Купить":
        answer+=("Отправьте желаемое число токенов")
        message_token=1
        keyboard = [['🔙Меню']]
    elif command=="🔻Продать":
        answer+=("Отправьте желаемое число токенов")
        message_balance=1
        keyboard = [['🔙Меню']]
    elif command=="💰Balance":
        answer+=("Свободные средства: *{}*".format(balance))
        keyboard = [['🔹Пополнение', '🔻Вывод'],
                       ['🔙Меню']]
    elif command=="📜About":
        answer+=("Что же такое *Gram*?🤔\n\n*Gram* - это новая криптовалюта Павла Дурова. Через пару месяцев она *перевернет* мировой финансовый рынок😱\n\nВкладываться в их токены в одиночку - *гиблая затея*, потому что минимальная ставка сейчас - *20.000.000$*\n\nКак же урвать кусок *бурно растущего пирога*?\n\nМы предлагаем *нью-скул* инвестиции в эту крипту:\n\nКаждый инвестор покупает лишь часть *Gram'a*, а мы распределяем доходы и выплачиваем проценты.\n\n*Ты ни от кого не зависишь* - средства разделены по хранилищам😍\n\n*Кто мы такие?*🤔\nМы представители инвестиционной компании *Oracle Venture Fund* в России. Объединяем инвесторов = *вкладываем в будущее*\n\n*А доказательства?*🙁\nРадость и отзывы инвесторов-@...")
    elif command=="👥Company":
        answer+=("Статус: *{}*".format(tick))
        answer+=("\nСоинвесторы: *{}*".format(referals))
        if parent_id!='000000000':
            answer+=("\nВас пригласил: *{}*".format(parent_id))
        answer+=("\n\nTON Gram - *огромное* экономическое событие. *Одиноким* инвесторам *сложно* зайти на рынок.\n\nМы поощряем *совместные инвестиции*: поделись с коллегами этой ссылкой - https://t.me/TONOGRAMbot?start="+str(user)+"\n\nВы вместе получаете *бонусные токены*, а тебе присваиваются новые *статусы*.\n\nУсловия получения статусов:\n*Клерк* - начальный статус\n*Партнер*- 1+ соинвесторов\n*Менеджер* - 10+ соинвесторов\n*Управленец* - 25+ соинвесторов\n*Директор* - 50+ соинвесторов")
    elif command=="🔹Пополнение":
        answer+=("Выберите платежную систему")
        keyboard = [['Сбербанк', 'Qiwi'],
                       ['Я.Деньги', 'Webmoney'],
                                      ['🔙Меню']]
    elif command=="Qiwi":
        answer+=('Для пополнения Вашего баланса переведите нужную сумму здесь:\nhttps://qiwi.com/payment/form/99?extra%5B%27account%27%5D=71919191923&amountInteger=1&amountFraction=0&extra%5B%27comment%27%5D='+user+'&currency=643&blocked[0]=account&&blocked[1]=comment')
    elif command=="🔻Вывод":
        answer+=("Выберите сумму")
        keyboard = [['50', '100', '300'],
                       ['500', '750', '1000'],
                       ['2000', '5000', '10000'],
                       ['🔙Меню']]
    elif command=="🔙Меню":
        answer+=("Здравствуй, *инвестор*👤 \n\nЯ - новый бот для обмена криптовалюты *TON*💎\n\nВсе очень просто: *вы покупаете токены, а я слежу за их курсом и возвращаю с процентом*📊")
        message_token=0
        message_balance=0
    elif command.isdigit():
        command=int(command)
        if message_token==1:
            if(balance-command*price>=0):
                balance-=command*price
                tokens+=command
                message_token=0
                message_balance=0
                answer+=("Успешно куплено *{}* токенов\nСвободные средства: *{}* руб\nВсего токенов: *{}*".format(command, balance, tokens))
            else:
                answer+=("Вы не можете купить столько токенов. Попробуйте еще раз.")
        if message_balance==1:
            if(tokens-command>=0):
                balance+=command*price
                tokens-=command
                message_token=0
                message_balance=0
                answer+=("Успешно продано *{}* токенов\nСвободные средства: *{}* руб\nВсего токенов: *{}*".format(command, balance,tokens))
            else:
                answer+=("Вы не можете продать столько токенов. Попробуйте еще раз.")

    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('UPDATE subs SET balance=? WHERE id=?',[balance,user])
    c.execute('UPDATE subs SET tokens=? WHERE id=?',[tokens,user])
    c.execute('UPDATE subs SET referals=? WHERE id=?',[referals,user])
    c.execute('UPDATE subs SET status=? WHERE id=?',[status,user])
    conn.commit()
    conn.close()
    reply_markup = ReplyKeyboardMarkup(keyboard)
    bot.send_message(chat_id=user, text=answer, reply_markup=reply_markup,parse_mode=ParseMode.MARKDOWN)


#####################################HANDLERS###################################
start_command_handler = CommandHandler('start', startCommand, pass_args=True)
text_message_handler = MessageHandler(Filters.text, textMessage)
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
#####################################UPDATES####################################
updater.start_polling(clean=True)
updater.idle()
