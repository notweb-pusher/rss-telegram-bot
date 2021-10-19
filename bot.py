from bs4 import BeautifulSoup
import requests
import myconfig
import telebot
import schedule
import datetime


# These 3 functions just prettify the data from xml
def get_time(obj: str) -> str:
    return ' '.join(obj.split()[1:-1])

def make_news(obj) -> str:
    '''
    Recieves some bs object and formats to string without useless data
    '''

    title = obj.title.text
    description = obj.description.text
    link = obj.link.text
    pub_date = get_time(obj.pubDate.text)

    return (f"The passage is about {title} \nTime : {pub_date}\nReview : {description}\n"
            f"If you are interested click the {link}")

def to_datetime(obj : str) -> datetime:
    tokens = obj.split()
    month_name = tokens[1]
    month_int = datetime.datetime.strptime(month_name, "%b").month
    tokens[1] = str(month_int)
    new_obj = ' '.join(tokens)
    date = datetime.datetime.strptime(new_obj, "%d %m %Y %H:%M:%S") 
    return date

# Updates the recent post date in myconfig.py
def update_config(date):
    with open("myconfig.py", "r+") as f:
        data =f.readlines()
        f.seek(0)
        f.truncate()
        data[0] = f"LAST_PUBLICATION = '{date}'\n"
        f.writelines(data)

last_update = to_datetime(myconfig.LAST_PUBLICATION)

def main():

    bot = telebot.TeleBot(myconfig.TOKEN)

    def update_poll(): 
        global last_update

        url = requests.get(myconfig.LINK)
        obj = BeautifulSoup(url.content, 'xml')
        
        group_url = f"https://api.telegram.org/bot{myconfig.TOKEN}/sendMessage"

        for el in obj.find_all('item')[::-1]: 
            if to_datetime(get_time(el.pubDate.text))  > last_update:
                last_update = to_datetime(get_time(el.pubDate.text))
                update_config(get_time(el.pubDate.text))
                requests.get(group_url , params = dict(chat_id = myconfig.ID, text = make_news(el))) 
    
    #  Every 30 minutes sends the response and posts news if there are some 
    schedule.every(30).minutes.do(update_poll)

    while True:
        schedule.run_pending()

if __name__ == "__main__":
    main()