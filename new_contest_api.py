
from flask import Flask, request
from flask_restful import Resource, Api
from bs4 import BeautifulSoup
import urllib2
import json
import os

app = Flask(__name__)
api = Api(app)

'''
scraping codechef and creating a dictionary for json object
'''

url = 'https://www.codechef.com/contests'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page,"html.parser")

result = []
resultSet = {"present_contests":[],"upcoming_contests":[]}
tableList = soup.findAll("table",attrs = {"class":"dataTable"})  #listofAllLinks

present_contests = tableList[0].findAll("tr")  #present contests
for contest in present_contests[1:]:
    event_details_row = contest.findAll("td")
    code = event_details_row[0].string
    name = event_details_row[1].string
    start_time = event_details_row[2].string
    end_time = event_details_row[3].string
    contest_url = "www.codechef.com/" + code
    resultSet["present_contests"].append({"code":code,"platform":"codechef","name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})

upcoming_contests = tableList[1].findAll("tr")  #upcoming contests
for contest in upcoming_contests[1:]:
    event_details_row = contest.findAll("td")
    code = event_details_row[0].string
    name = event_details_row[1].string
    start_time = event_details_row[2].string
    end_time = event_details_row[3].string
    contest_url = "www.codechef.com/" + code
    resultSet["upcoming_contests"].append({"code":code,"platform":"codechef","name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})


'''
adding codeforces events without scraping using Codeforces api
key : 0ea5291d2d8b726c0b8c3aeb1b5288192f5db373
secret : bad1aae399dafa014e3d9cc53a35c6a3c2ace9df
'''

url = 'http://codeforces.com/api/contest.list'
page = urllib2.urlopen(url)
data = json.load(page)
allevents = data["result"]
for event in allevents:
    if(event["phase"] == "FINISHED"):
        break
    if(event["phase"] == "BEFORE"):
        code = event["id"]
        name = event["name"]
        start_time = event["startTimeSeconds"]
        end_time = event["durationSeconds"]
        platform = "codeforces"
        contest_url = 'http://codeforces.com/contest/' + str(code)
        resultSet["upcoming_contests"].append({"code":code,"platform":platform,"name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})
    else:
        code = event["id"]
        name = event["name"]
        start_time = event["startTimeSeconds"]
        end_time = event["durationSeconds"]
        platform = "codeforces"
        contest_url = 'http://codeforces.com/contest/' + str(code)
        resultSet["present_contests"].append({"code":code,"platform":platform,"name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})

'''
adding HackerEarth events using Hackerearth Chrome Extension URL which returns a JSON object
url : "https://www.hackerearth.com/chrome-extension/events/"
'''

url = "https://www.hackerearth.com/chrome-extension/events/"
page = urllib2.urlopen(url)
data = json.load(page)
allevents = data["response"]
for event in allevents:
    if(event["status"] == "UPCOMING"):
        code = event["challenge_type"]
        name = event["title"]
        start_time = event["start_timestamp"]
        end_time = event["end_timestamp"]
        platform = "hackerearth"
        contest_url = event["url"]
        resultSet["upcoming_contests"].append({"code":code,"platform":platform,"name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})
    else:
        code = event["challenge_type"]
        name = event["title"]
        start_time = event["start_timestamp"]
        end_time = event["end_timestamp"]
        platform = "hackerearth"
        contest_url = event["url"]
        resultSet["present_contests"].append({"code":code,"platform":platform,"name":name,"start_time":start_time,"end_time":end_time,"contest_url":contest_url})


class TodoSimple(Resource):
    def get(self):
        return {"result": resultSet}


api.add_resource(TodoSimple, '/')


port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
