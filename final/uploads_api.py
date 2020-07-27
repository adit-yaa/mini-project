import argparse
import os
import re
import requests
import csv

import convert2csv

import flask
from flask import request, jsonify

import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRETS_FILE = 'client_secret.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  creds=None
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
  return build(API_SERVICE_NAME, API_VERSION, credentials = creds)

# retrieves all the plalists on a channel
def get_my_uploads_list():
  channels_response = youtube.channels().list(
    mine=True,
    part='contentDetails'
  ).execute()

  for channel in channels_response['items']:
    return channel

  return None

# retrieves all the videos in a playlist
def list_my_uploaded_videos(uploads_playlist_id):
  videos=[]
  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=uploads_playlist_id,
    part='snippet',
    maxResults=5
  )
  print('Videos in list %s' % uploads_playlist_id)
  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    for playlist_item in playlistitems_list_response['items']:
      title = playlist_item['snippet']['title']
      video_id = playlist_item['snippet']['resourceId']['videoId']
      print('%s (%s)' % (title, video_id))
      videos.append(playlist_item)
    playlistitems_list_request = youtube.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response)
    return videos

# retrieves all the comments on a video
def get_comment_threads(video_id):
  results = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    textFormat="plainText",
  ).execute()
  return results["items"]

app = flask.Flask(__name__)
app.config["DEBUG"] = True

youtube = get_authenticated_service()

# uploads_playlist_id = get_my_uploads_list()
# if uploads_playlist_id:
#   list_my_uploaded_videos(uploads_playlist_id)
# else:
#   print('There is no uploaded videos playlist for this user.')
@app.route('/channel', methods=['GET'])
def channel():
  return jsonify(get_my_uploads_list())

@app.route('/<uploads_playlist_id>/videos', methods=['GET'])
def playlists(uploads_playlist_id):
  return jsonify(list_my_uploaded_videos(uploads_playlist_id))

@app.route('/<video_id>/comments', methods=['GET'])
def comments(video_id):
  return jsonify(get_comment_threads(video_id))


@app.route('/<video_id>/analyse_comments', methods=['GET'])
def analyse_comments(video_id):
  convert2csv.convert2CSV(video_id)
  # os.system('python3 mini_model.py')
  return jsonify(convert2csv.convert2dict())

app.run(debug=True)