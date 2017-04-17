#!/usr/bin/env python3

from flask import Flask, request
from flask_restful import Resource, Api
from bs4 import BeautifulSoup
import urllib2
import json
import os
from time import strptime,strftime,mktime,gmtime,localtime

app = Flask(__name__)
api = Api(app)

result = []
resultSet = {"present_contests":[],"upcoming_contests":[]}



page = urlopen("http://www.codechef.com/contests")
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


resultSet["upcoming_contests"] = sorted(resultSet["upcoming_contests"], key=lambda k: strptime(k['StartTime'], "%a, %d %b %Y %H:%M"))
resultSet["present_contests"] = sorted(resultSet["upcoming_contests"], key=lambda k: strptime(k['EndTime'], "%a, %d %b %Y %H:%M"))

class TodoSimple(Resource):
    def get(self):
        return {"result": resultSet}


api.add_resource(TodoSimple, '/')


port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
