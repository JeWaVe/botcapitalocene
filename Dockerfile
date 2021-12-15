FROM python:3.8-alpine

RUN pip3 install tweepy
RUN mkdir /usr/local/bin/bot
ADD bot.py /usr/local/bin/bot/

ENTRYPOINT [ "python", "/usr/local/bin/bot/bot.py" ]