from django.http import HttpResponse
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI = 'http://localhost:8000/rest/v1/calendar/redirect/'

def GoogleCalendarInitView(request):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def GoogleCalendarRedirectView(request):
    state = request.session['oauth_state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(
        authorization_response=request.build_absolute_uri()
    )
    credentials = flow.credentials

    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    calendar_list = service.calendarList().list().execute()

    calendar_id = calendar_list['items'][0]['id']

    events = service.events().list(calendarId=calendar_id).execute()

    events_list = []
    if not events['items']:
        return HttpResponse(json.dumps({"message": "No events found"}))
    else:
        for event in events['items']:
            events_list.append(event)

    return HttpResponse(json.dumps({"events": events_list}))