#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import datetime
import json
from twilio.rest import Client
import os


ceburl = "https://cebcare.ceb.lk/Incognito/DemandMgmtSchedule"


def getVerificationToken():
    r = requests.get(ceburl)
    soup = BeautifulSoup(r.text, 'lxml')
    requestverificationToken = soup.find(
        'input', attrs={'name': '__RequestVerificationToken'})['value']
    return requestverificationToken, r.cookies.get_dict()


def getDetails(cookies, token):
    # just getting the date and time to post
    startTime = datetime.date.today()
    endTime = startTime + datetime.timedelta(days=1)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'RequestVerificationToken': token,
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://cebcare.ceb.lk',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://cebcare.ceb.lk/Incognito/DemandMgmtSchedule',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Cache-Control': 'max-age=0',
    }

    data = {
        'StartTime': startTime,
        'EndTime': endTime,
    }

    response = requests.post('https://cebcare.ceb.lk/Incognito/GetLoadSheddingEvents',
                             headers=headers, cookies=cookies, data=data)
    payload = json.loads(response.text)
    # print(payload[0]['startTime'])
    message = f"stupid powercut for today {startTime}\n\n start time -> {payload[0]['startTime']}.\n end time -> {payload[0]['endTime']}"
    return message


reqtoken, cookies = getVerificationToken()
message = getDetails(cookies, reqtoken)

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
phone_number = os.environ['MY_PHONE_NUMBER']

client = Client(account_sid, auth_token)

from_whatsapp_number = 'whatsapp:+14155238886'
to_whatsapp_number = phone_number

# fetch the stupid stuff

message = client.messages.create(
    body=message,
    from_=from_whatsapp_number,
    to=to_whatsapp_number
)

print(message.sid)
