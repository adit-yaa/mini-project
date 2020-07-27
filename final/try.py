"""
Created on Thu May 28 05:53:35 2020

@author: Adityaa
"""
import os
import re
import requests
import argparse
import csv

import flask

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import mini

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.secret_key = 'lungi-dhoti'

@app.route('/')
def index():
  if 'credentials' not in flask.session:
    credential_present=0
  else:
    credential_present=1
  return flask.render_template('index.html', credential_present=str(credential_present))

@app.route('/list')
def video():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')
  return flask.render_template('videos.html')

@app.route('/<video_id>')
def analyse_page(video_id):
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')
  return flask.render_template('analyse_comments.html')

@app.route('/channel')
def get_channel_contents():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

  content_details = flask.jsonify(youtube.channels().list(mine=True, part='contentDetails').execute())
  # Save credentials back to session in case access token was refreshed.
  flask.session['credentials'] = credentials_to_dict(credentials)
  return content_details

@app.route('/channel/<playlist_id>')
def get_playlist_contents(playlist_id):
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=playlist_id,
    part='snippet',
    maxResults=5
  )
  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    # Save credentials back to session in case access token was refreshed.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**playlistitems_list_response)

@app.route('/<video_id>/comments')
def get_video_comments(video_id):
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

  comments = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    textFormat="plainText",
  ).execute()

  # Save credentials back to session in case access token was refreshed.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(comments['items'])

@app.route('/<video_id>/comments/analyse', methods = ['POST'])
def analyse(video_id):
  toxic_count=0
  severe_toxic_count=0
  obscene_count=0
  threat_count=0
  insult_count=0
  identity_hate_count=0
  positive=0
  negative=0

  toCSV=[]
  values = flask.request.get_json()
  required = ['id','comment_text']
  for value in values:
    if not all(k in value for k in required):
      return 'Missing values', 400
  try:
    keys = values[0].keys()
    with open('test.csv', 'w') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(values)
    labels = ['id','toxic', 'severe_toxic','obscene','threat','insult','identity_hate']
    sample_init={key: 0.5 for key in labels}
    for value in values:
      sample_init['id']=value['id']
      toCSV.append(sample_init)
    keys = toCSV[0].keys()
    with open('sample_submission.csv', 'w') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(toCSV)
    os.system('python3 model.py')
    FILE="demo.csv"
    with open(FILE) as f:
      a = [{k: v for k, v in row.items()}for row in csv.DictReader(f, skipinitialspace=True)]
      for comment in a:
        point=0
        if float(comment['toxic'])>0.45:
          toxic_count+=1
        else:
          point+=1

        if float(comment['severe_toxic'])>0.45:
          severe_toxic_count+=1
        else:
          point+=1

        if float(comment['obscene'])>0.45:
          obscene_count+=1
        else:
          point+=1

        if float(comment['threat'])>0.45:
          threat_count+=1
        else:
          point+=1

        if float(comment['insult'])>0.45:
          insult_count+=1
        else:
          point+=1

        if float(comment['identity_hate'])>0.45:
          identity_hate_count+=1
        else:
          point+=1
        if point==len(labels)-1:
          positive+=1
        else:
          negative+=1
    return flask.jsonify(toxic=str(toxic_count), severe_toxic=str(severe_toxic_count), obscene=str(obscene_count), threat=str(threat_count), insult=str(insult_count), identity_hate=str(identity_hate_count), positive=str(positive), negative=str(negative)), 201
  except:
    return flask.jsonify(toxic=str(toxic_count), severe_toxic=str(severe_toxic_count), obscene=str(obscene_count), threat=str(threat_count), insult=str(insult_count), identity_hate=str(identity_hate_count), positive=str(positive), negative=str(negative)), 201
      

@app.route('/run_model', methods = ['GET'])
def run_model():
  os.system('python3 mini_model.py')
  FILE="demo.csv"
  with open(FILE) as f:
    a = [{k: v for k, v in row.items()}for row in csv.DictReader(f, skipinitialspace=True)]
  return flask.jsonify(data=a, message="Output Produced")

@app.route('/analyse/comments/results', methods = ['GET'])
def get_results():
  try:
    FILE="demo.csv"
    with open(FILE) as f:
      a = [{k: v for k, v in row.items()}for row in csv.DictReader(f, skipinitialspace=True)]
      os.remove(FILE)
    return flask.jsonify(data=a)
  except:
    return "Oops please hit /run_model first!", 404

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('video'))


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return flask.redirect(flask.url_for('index'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)