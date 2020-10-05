import schedule
import time
import datetime
import requests
import json
import random

def job():
    try:
        # choose company at random to scrape news for, alternatively change company_name in params
        company = random.choice(['facebook', 'google', 'apple', 'dyson', 'microsoft', 'intel'])

        articles_request = requests.get("http://localhost:5000/api/v1/news/scrape", params={"company_name": company, "start_date":"10-10-2019", "bodies": "true"})
        articles_data = articles_request.json()

        # save the articles into db by making an POST call to our api endpoint
        save_articles = requests.post("http://localhost:5000/api/v1/news", json=articles_data, headers={'Content-Type': 'application/json', 'Accept':'application/json'})


        if save_articles.status_code == 200:
            #log to a file
            print(f"Saved to db at {datetime.datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
        else:
            #log to a file
            print("Something went wrong scraping news for company: {company} at {datetime.datetime.now().strftime('%d %B %Y, %H:%M:%S')}")

    except Exception as e:
        print("Log to a file the exeception", e)


# schedule.every(5).minutes.do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)

# schedule.every().day.at("19:15").do(job)
schedule.every(2).minutes.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
    print(datetime.datetime.now().strftime('%d %B %Y, %H:%M:%S'))