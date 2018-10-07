import requests
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sys
import unicodedata

with open('./stopwords_en.txt', "r") as words:
    stop_words = words.read().split()

url = "https://api.meaningcloud.com/summarization-1.0"

key = "feaa0cf15fbd67458bfe4b906f04fbe8"

text = """Good morning and welcome to day two of the Annual Banking and Financial Services Conference. It's my pleasure to have all of you here. Why don't I start off by maybe asking both of you, Johnny and Selena. People on the sell side like me and investors have been focused on this whole operating leverage thing for such a long time. At the same time, we certainly want to make sure that the stuff that you're eliminating is inefficiency as opposed to investment for growth. What was the process that you went through in order to make sure that what you were eliminating was a waste as opposed to the real growth spending?"""

text = text.replace("’", "'")

tokenized_text = word_tokenize(text)

filtered_text = [word for word in tokenized_text if word not in stop_words]

text = " ".join(filtered_text)

payload = "key={}&txt={}&url={}&sentences=5".format(key, text, url)
headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf-8'}

response = requests.request("POST", url, data=payload, headers=headers)

summary = json.loads(response.text)['summary']
print(summary)
