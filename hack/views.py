from __future__ import print_function
from django.shortcuts import render
from django.http import JsonResponse
from .models import Meeting
import io
import requests
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import maya
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from django.contrib.auth.decorators import login_required

with open('./hack/stopwords_en.txt', "r") as words:
    stop_words = words.read().split()

def login(request):
    return render(request, "hack/login.html", {})

def index(request):
    if request.POST and request.FILES:
        speech_file = request.FILES['audio_file'].name
        # text_data = json.dumps([[2, 'This meeting is conducted to discuss. Decreasing sales of the company. '], [1, 'So we need to follow some steps in order to increase the sales or do we need to increase our social media game? We need to focus more on social media platforms, like '], [2, 'Facebook Instagram and '], [1, 'advertise there more according to section. Also, we are thinking of conducting a session on 23rd October 2018 to discuss the sales of the company so that every employee of the company knows what is the status of the cells right now is a session compulsory. Yes. It is compulsory for every employee of the company. Okay, then. ']])
        text_data = json.dumps(transcribe_file(speech_file))
        text_data1 = transcribe_file(speech_file)
        today_date = datetime.date.today()
        today_date.strftime('%Y/%m/%d')
        leader_name = request.POST['leader_name']
        agenda = request.POST['agenda']
        nopersons = request.POST['nopersons']
        transcripts = ""
        for i in text_data1:
            transcripts += "Speaker" + " " + str(i[0]) + ": " + i[1]

        m = Meeting(leader_name=leader_name,
                agenda=agenda,
                date=today_date,
                transcripts=transcripts,
                no_of_persons=nopersons
        )
        m.save()
        return render(request, 'hack/dashboard.html', {'text_data': text_data, 'leader_name': leader_name})
    return render(request, 'hack/dashboard.html', {'text_data': 'no'})

def dash2(request):
    if request.POST:
        text = request.POST['text']
        leader_name = request.POST['data_id']
        m = Meeting.objects.all().filter(leader_name=leader_name)
        speakers_data = json.loads(text)
        speakers_notes = {}
        speakers_sentiment = {}
        doc = ""
        summary = ""
        for key, value in speakers_data.items():
            doc += value;
            speakers_notes[key] = summarizer(value)
            speakers_sentiment[key] = analyze(value)
            summary += "Speaker " + str(key) + ": " + summarizer(value)

        dates = date_retrieval(doc)
        print(dates)
        return render(request, 'hack/summary.html', {'summarized_text': json.dumps(speakers_notes), 'dates': json.dumps(dates), 'speakers_sentiment': json.dumps(speakers_sentiment)})
    return render(request, 'hack/summary.html', {'summarized_text': 'no', 'dates': 'no', 'speakers_sentiment': 'no'})


def speech_to_text(request):

    data = {'text': "text"}
    return JsonResponse(data)


def transcribe_file(speech_file):
    """Transcribe the given audio file."""

    client = speech.SpeechClient()


    gcs_uri = 'gs://voicex/' + speech_file
    audio = speech.types.RecognitionAudio(uri=gcs_uri)

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-IN',
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        enable_automatic_punctuation=True)

    print('Waiting for operation to complete...')
    response = client.recognize(config, audio)

    # The transcript within each result is separate and sequential per result.
    # However, the words list within an alternative includes all the words
    # from all the results thus far. Thus, to get all the words with speaker
    # tags, you only have to take the words list from the last result:
    result = response.results[-1]

    words_info = result.alternatives[0].words

    chat = []
    previous_speaker = 0
    str = ''
    for word_info in words_info:
        speaker = word_info.speaker_tag
        if previous_speaker != speaker:
            if str != '':
                chat.append([previous_speaker, str])
            str = ''
            str += word_info.word + ' '
            previous_speaker = speaker
        else:
            str += word_info.word + ' '

    chat.append([previous_speaker, str])
    return chat

def summarizer(text):
    url = "https://api.meaningcloud.com/summarization-1.0"

    key = "YOUR_OWN_KEY"

    text = text.replace("’", "'")

    tokenized_text = word_tokenize(text)

    filtered_text = [word for word in tokenized_text if word not in stop_words]

    text = " ".join(filtered_text)

    payload = "key={}&txt={}&url={}&sentences=5".format(key, text, url)
    headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf-8'}

    response = requests.request("POST", url, data=payload, headers=headers)

    summarized_text = json.loads(response.text)['summary']
    return summarized_text


def date_retrieval(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(u'{}'.format(text))

    dates = []
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            dates.append(ent.text)

    return(dates)

def insert_in_calendar(request):
    if request.POST:

        date = request.POST['date']
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        store = file.Storage('./hack/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('./hack/credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('calendar', 'v3', http=creds.authorize(Http()))

        s = maya.when(date)
        date = s.datetime().strftime("%Y-%m-%d")

        event = {
        	'description': 'VoiceX Meeting Notes',
        	'start': {
        		'date': date,
        		'timeZone': 'Asia/Kolkata',
        	},
        	'end': {
        		'date': date,
        		'timeZone': 'Asia/Kolkata',
        	},
        	'recurrence': [
        		'RRULE:FREQ=DAILY;COUNT=2'
        	],
        	'reminders': {
        		'useDefault': False,
        		'overrides': [
        			{'method': 'email', 'minutes': 24 * 60},
        			{'method': 'popup', 'minutes': 10},
        		],
        	},
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return JsonResponse({"foo": "booked"})
    return JsonResponse({"foo": "bar"})

def past_meets(request):
    m = Meeting.objects.all()
    return render(request, 'hack/past_meetings.html', {'m': m})

def past_meets_details(request, id):
    m = Meeting.objects.all().filter(id=id)[0]
    print(m)
    return render(request, 'hack/past_meetings_details.html', {'m': m})


def analyze(content):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()

    document = types.Document(
        content=content,
        type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    # Print the results
    return annotations.document_sentiment.score
