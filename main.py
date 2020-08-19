import telebot

import datetime
from pycbrf import ExchangeRates
from newsapi import NewsApiClient

date = datetime.datetime.now()  # текущие дата и время
now = date.strftime("%Y-%m-%d")

# Список адресов сайтов СМИ, в которых бот будет искать статьи
mass_media = 'ria.ru, iz.ru, vedomosti.ru, lenta.ru, tass.ru,' \
             'gazeta.ru, fontanka.ru, rg.ru, kommersant.ru'

# Текст, который бот будет выдавать по просьбе пользователя вывести доступные команды
commands = """

Доступные комманды:

Курс доллара
Курс евро

По следующим запросам отправит 20 последних новостей:

Ведомости
Газетару
Лентару
Коммерсант
Тасс
Известия
Риа
Росгазетару

Осуществит поиск новостей за текущие сутки по ключевому слову:
Поиск ключевое_слово

Для получения ссылки на новость пишите:
Ссылка номер_новости
"""

# Токен бота
bot = telebot.TeleBot('Токен_бота')

# Токен  News Api https://newsapi.org/
newsapi = NewsApiClient(api_key='API_КЛЮЧ')

url_list = []  # список, в котором будут сохраняться ссылки на найденные статьи


def find_articles(day, domain, key_word):
    """Возвращает массив статей (заголовок, ссылка, содержание),
        найденных по заданной дате, доменам, ключевым словам """
    all_articles = newsapi.get_everything(q=key_word,
                                          domains=domain,
                                          from_param=day,
                                          to=day,
                                          language='ru',
                                          sort_by='publishedAt',
                                          page=1)
    return all_articles


def print_news(articles):
    """Обрабатывает данные и красиво их оформляет для выдачи пользователю"""
    news = ""
    number = 1
    global url_list
    url_list = []
    for i in articles['articles']:
        new = "{}) {} \n\n".format(str(number), i['title'])
        url_list.append(i['url'])
        news = news + new
        number = number + 1
    news = news + "\n  Для получения ссылки на новость пишите: Ссылка номер_новости"
    return news


def bot_send_message(message, media_name):
    """Бот отправляет пользователю найденные статьи по заданному СМИ"""
    articles = find_articles(now, media_name, '')
    print_f_news = print_news(articles)
    bot.send_message(message.from_user.id, print_f_news)


# узнать курс
def find_value(currency):
    """Возвращает текущий курс"""
    rates = ExchangeRates(now)
    name = rates[currency].name
    value = rates[currency].value
    answer = str(name) + " " + str(value)
    return answer


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """Бот ищет в сообщениях пользователя ключевые слова,
        если находит - присылает соответствующее сообщение"""
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Чтобы увидеть список комманд, напиши /help")

    elif "доллар" in message.text.lower():
        value = find_value("USD")
        bot.send_message(message.from_user.id, value)

    elif "евро" in message.text.lower():
        value2 = find_value("EUR")
        bot.send_message(message.from_user.id, value2)

    elif "лентару" in message.text.lower():
        bot_send_message(message, 'lenta.ru')

    elif "ведомости" in message.text.lower():
        bot_send_message(message, 'vedomosti.ru')

    elif "риа" in message.text.lower():
        bot_send_message(message, 'ria.ru')

    elif "известия" in message.text.lower():
        bot_send_message(message, 'iz.ru')

    elif "тасс" in message.text.lower():
        bot_send_message(message, 'tass.ru')
    elif "газетару" in message.text.lower():
        bot_send_message(message, 'gazeta.ru')
    elif "росгазетару" in message.text.lower():
        bot_send_message(message, 'rg.ru')
    elif "коммерсант" in message.text.lower():
        bot_send_message(message, 'kommersant.ru')

    elif "ссылка" in message.text.lower():
        try:
            index = int(message.text[7:]) - 1
            url_news = url_list[index]
            bot.send_message(message.from_user.id, url_news)
        except:
            bot.send_message(message.from_user.id, "Напиши: 'ссылка номер_ссылки' ")

    elif "поиск" in message.text.lower():
        find_w = str(message.text[6:])
        articles = find_articles(now, mass_media, find_w)
        print_f_news = print_news(articles)
        try:
            if len(articles['articles']) == 0:
                bot.send_message(message.from_user.id, "Ничего не найдено, попробуйте снова")
            else:
                bot.send_message(message.from_user.id, print_f_news)
        except:
            bot.send_message(message.from_user.id, "Ошибка, попробуйте снова")


    elif message.text == "/help":
        bot.send_message(message.from_user.id, commands)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=0)
