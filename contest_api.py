from flask import Flask, request
from flask_restful import Resource, Api
from bs4 import BeautifulSoup
import requests
from time import strptime,strftime,mktime,gmtime,localtime
import json
import os

app = Flask(__name__)
api = Api(app)



result = []
resultSet = {"present_contests":[],"upcoming_contests":[]}

def get_duration(duration):
    days = duration/(60*24)
    duration %= 60*24
    hours = duration/60
    duration %= 60
    minutes = duration
    ans=""
    if days==1: ans+=str(days)+" day "
    elif days!=0: ans+=str(days)+" days "
    if hours!=0:ans+=str(hours)+"h "
    if minutes!=0:ans+=str(minutes)+"m"
    return ans.strip()


# CodeChef Contest Fetching

page = requests.get("http://www.codechef.com/contests").text
soup = BeautifulSoup(page, "html.parser")

statusdiv = soup.findAll("table", attrs = {"class": "dataTable"})
headings = soup.findAll("h3")
contest_tables = {"Future Contests": [], "Present Contests": []}
for i in range(len(headings)):
    if headings[i].text != "Past Contests":
        contest_tables[headings[i].text] = statusdiv[i].findAll("tr")[1:]

for upcoming_contest in contest_tables["Future Contests"]:
    details = upcoming_contest.findAll("td")
    start_time = strptime(details[2].text, "%d %b %Y %H:%M:%S")
    end_time = strptime(details[3].text, "%d %b %Y %H:%M:%S")
    duration = get_duration(int((mktime(end_time) - mktime(start_time)) / 60))
    resultSet["upcoming_contests"].append({"Name":  details[1].text,
                              "url": "http://www.codechef.com" + details[1].a["href"],
                              "StartTime": strftime("%a, %d %b %Y %H:%M", start_time),
                              "EndTime": strftime("%a, %d %b %Y %H:%M", end_time),
                              "Duration": duration,
                              "Platform": "CODECHEF"})

for present_contest in contest_tables["Present Contests"]:
    details = present_contest.findAll("td")
    end_time = strptime(details[3].text, "%d %b %Y %H:%M:%S")
    resultSet["present_contests"].append({"Name":  details[1].text,
                             "url": "http://www.codechef.com" + details[1].a["href"],
                             "EndTime": strftime("%a, %d %b %Y %H:%M", end_time),
                             "Platform": "CODECHEF"})


# HackerEarth Contest Fetching

cur_time = localtime()
ref_date =  strftime("%Y-%m-%d",  localtime(mktime(localtime())   - 432000))
duplicate_check=[]

page = requests.get("https://www.hackerearth.com/chrome-extension/events/")
data = page.json()["response"]
for item in data:
    start_time = strptime(item["start_tz"].strip()[:19], "%Y-%m-%d %H:%M:%S")
    end_time = strptime(item["end_tz"].strip()[:19], "%Y-%m-%d %H:%M:%S")
    duration = get_duration(int(( mktime(end_time)-mktime(start_time) )/60 ))
    duplicate_check.append(item["title"].strip())

    if item["challenge_type"]=='hiring':challenge_type = 'hiring'
    else: challenge_type = 'contest'

    if item["status"].strip()=="UPCOMING":
        resultSet["upcoming_contests"].append({ "Name" :  item["title"].strip()  , "url" : item["url"].strip() , "StartTime" : strftime("%a, %d %b %Y %H:%M", start_time),"EndTime" : strftime("%a, %d %b %Y %H:%M", end_time),"Duration":duration,"Platform":"HACKEREARTH","challenge_type": challenge_type  })
    elif item["status"].strip()=="ONGOING":
        resultSet["present_contests"].append({ "Name" :  item["title"].strip()  , "url" : item["url"].strip() , "EndTime" : strftime("%a, %d %b %Y %H:%M", end_time),"Platform":"HACKEREARTH","challenge_type": challenge_type  })



resultSet["upcoming_contests"] = sorted(resultSet["upcoming_contests"], key=lambda k: strptime(k['StartTime'], "%a, %d %b %Y %H:%M"))
resultSet["present_contests"] = sorted(resultSet["present_contests"], key=lambda k: strptime(k['EndTime'], "%a, %d %b %Y %H:%M"))





class TodoSimple(Resource):
    def get(self):
        return {"result": resultSet}


api.add_resource(TodoSimple, '/')


port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
