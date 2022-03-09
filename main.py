from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler,Filters
import telegram
from telegram import ParseMode, User,Bot
import time
import datetime, time, pytz
from datetime import date
from lxml import html
import requests, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('tonal-loader-343318-21656014eb9a.json', scope)
client = gspread.authorize(creds)

config = json.load(open('config.json','r'))
TOKEN = config['token']
data = []

url_exploder = config['url_exploder']
url_wallet = config['url_wallet']

xpath_url_exploder = '//*[@id="__next"]/div/main/div[2]/div[1]/div[1]/div/div[1]/span[1]/text()[2]'
xpath_url_wallet = '//*[@id="__next"]/div/div/main/div/div/div/div/div/div/div/div/table/tbody/tr/td[2]/span/span/text()'


def start(update, context):
    if update.message.chat.type == 'private':
        user = str(update.message.chat.username)
        if user not in data['users']:
            data['users'].append(user)
            message = "Chào mừng đến với bot của anh Hiếu đẹp trai"
            update.message.reply_text(message)

def add(update, context):
    if update.message.chat.type == 'private':
        user = str(update.message.chat.username)
        if user in data['users']:
            data['process'][user] = "wallet"
            message = "Send me your wallet Binance Chain"
            update.message.reply_text(message)
        else:
            message = "Please contact @ShadowCaptain"
            update.message.reply_text(message)


def price(update, context):
    if update.message.chat.type == "private":
        user = str(update.message.chat.username)
        if user in data['users']:
            chat_id = update.effective_chat.id
            message = ""
            exploder = requests.get(url_exploder)
            homepage = html.fromstring(exploder.content)
            get_price = homepage.xpath(xpath_url_exploder)
            price_update = get_price
            price =''.join([str(item) for item in price_update])
            vnd = float(price)*23000
            t = time.localtime()
            current_time = time.strftime("%H:%M", t)
            message += f"*Price at {current_time} UTC*\n\nUSD: {price}\nVND: {vnd}"
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            message = "Please contact @ShadowCaptain"
            update.message.reply_text(message)

def wallet(update, context):
    if update.message.chat.type == "private":
        user = str(update.message.chat.username)
        if user in data['users']:
            chat_id = update.effective_chat.id
            message = ""
            exploder = requests.get(url_exploder)
            homepage = html.fromstring(exploder.content)
            get_price = homepage.xpath(xpath_url_exploder)
            price_update = get_price
            price =''.join([str(item) for item in price_update])


            wallet = data['wallet'][user]
            exploder = requests.get(url_wallet+wallet)
            homepage = html.fromstring(exploder.content)
            get_balance = homepage.xpath(xpath_url_wallet)
            blance_update = get_balance
            blance = ''.join([str(item) for item in blance_update])

            usd = float(blance)*float(price)
            vnd = usd * 23000
            message += f"*Your wallet: {wallet}*\n\nBalance: {blance} BNB\nUSD: {usd}\nVND: {vnd}"
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            message = "Please contact @ShadowCaptain"
            update.message.reply_text(message)


def run(update, context):
    if update.message.chat.type == 'private':
        user = str(update.message.chat.username)
        if user in data['users']:
            chat_id = update.effective_chat.id
            message = ""
            message += f"*Bot automatic send staking reward every day 7:30*"
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
            context.job_queue.run_daily(callback_start, datetime.time(hour=6, minute=50, tzinfo=pytz.timezone('Asia/Ho_Chi_Minh')),
                                days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id, name=user)
        else:
            message = "Please contact @ShadowCaptain"
            update.message.reply_text(message)

def callback_start(context):
    chat_id=context.job.context
    message = ""
    user=context.job.name
    wallet=data['wallet'][user]
    d1 = date.today()
    exploder = requests.get(url_exploder)
    homepage = html.fromstring(exploder.content)
    get_price = homepage.xpath(xpath_url_exploder)
    price_update = get_price
    price =''.join([str(item) for item in price_update])

    exploder = requests.get(url_wallet+wallet)
    homepage = html.fromstring(exploder.content)
    get_balance = homepage.xpath(xpath_url_wallet)
    blance_update = get_balance
    blancex = ''.join([str(item) for item in blance_update]) # blancex: get blance on 6:50 every day

    time.sleep(2400)

    exploder = requests.get(url_wallet+wallet')
    homepage = html.fromstring(exploder.content)
    get_balance = homepage.xpath(xpath_url_wallet)
    blance_update = get_balance
    blancey = ''.join([str(item) for item in blance_update]) # blancex: get blance on 7:30 every day

    balance_save = float(blancey)-float(blancex)
    usd = balance_save * float(price)
    vnd = usd * 23000

    d2 = str(d1)
    balance_save_to_google_sheet = str(balance_save)
    sheet = client.open("Profits").worksheet("reward")
    data_sheet=sheet.get_all_records()
    next_edit_row_available=len(data_sheet)+2
    sheet.update_cell(next_edit_row_available,2,balance_save_to_google_sheet)
    sheet.update_cell(next_edit_row_available,1,d2)

    file_object = open('status.txt', mode="a")
    status = file_object.write(str(d1)+': '+str( balance_save)+'\n')
    message += f"*{d1}:* {balance_save} at price {price}$\n\nUSD: {usd}\nVND: {vnd}"
    file_object.close()
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)


def status(update, context):
    if update.message.chat.type == "private":
        user = str(update.message.chat.username)
        if user in data['users']:
            chat_id = update.effective_chat.id
            message = ""
            with open('status.txt') as f:
                for line in (f.readlines() [-30:]):
                    message += f"{line}"  
            context.bot.send_message(chat_id=chat_id, text=message)
        else:
            message = "Please contact @ShadowCaptain"
            update.message.reply_text(message)


def extra(update, context):
    if update.message.chat.type == 'private':
        user = str(update.message.chat.username)
        if data["process"][user] == 'wallet':
            data['wallet'][user] = update.message.text
            data['process'][user] = "finished"
            wallet_user = data['wallet'][user]
            json.dump(data,open('users.json','w'))
            message = '*Your wallet is:* {}'.format(wallet_user)
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


#//////////////////////////////////////////////////////////////////////////////////////////////#
if __name__ == '__main__':
    data = json.load(open('users.json','r'))
    updater = Updater(TOKEN,use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",start))
    dp.add_handler(CommandHandler("join",join))
    dp.add_handler(CommandHandler("add",add))
    dp.add_handler(CommandHandler("price",price))
    dp.add_handler(CommandHandler("wallet",wallet))
    dp.add_handler(CommandHandler("status",status))
    dp.add_handler(CommandHandler("run",run, pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text,extra))

    updater.start_polling()
    print("Bot Started")
    updater.idle()            
