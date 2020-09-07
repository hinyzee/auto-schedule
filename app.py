from flask import request, render_template
from flask import redirect, url_for, session, Flask
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
API_VERSION = 'v3'
API_SERVICE_NAME = 'calendar'
CLIENT_SECRETS_FILE = "client_secret_622606164667-6tlp0brae4cftg99tt4abo9lkbqdhe6h.apps.googleusercontent.com.json"
SCOPES = [
    'https://www.googleapis.com/auth/calendar'
]


app = Flask(__name__)
app.secret_key = 'yaYaYA'





@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301 # means that the url is updated
        return redirect(url, code=code)




# home page that sends the text data to confirmData
@app.route('/')
def home():

    # data we need to insert in the homepage
    data = {'error':''}

    # display error messages accordingly
    msg = [
        "Oops that page doesn't exist ;)",
        "Don't forget to do step 1 first!",
        "Double check if you're doing step 2 right?",
        "Hey don't ignore step 3 (-_-)",
        "You already logged in before sir"
    ]

    if 'e' in request.args and not request.args['e'].isalpha():
        ind = int(request.args['e'])
        if ind>=0 and ind<len(msg):
            data['error'] = msg[ind]



    if  'credentials' in session:
      data['revoke'] = "Revoke permission"

    # state is just a variable that is stored when oauth2callback has been run
    #if 'credentials' in session:
        #return render_template("home.html", data=data)

    # if haven't logged in yet, log in
    #return redirect('/authorize')

    return render_template("home.html", data=data)



# initialize the google login request
@app.route('/authorize', methods=['GET','POST'])
def authorize():

    if  'credentials' in session:
      return redirect("/?e=4")

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )


    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true'
    )


    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    url = """https://openidconnect.googleapis.com/v1/userinfo?
   response_type=code&
   client_id=622606164667-6tlp0brae4cftg99tt4abo9lkbqdhe6h.apps.googleusercontent.com&
   scope=openid%20email&
   redirect_uri=https%3A//oauth2.example.com/callback&
   state=dacd13213lk&
   nonce=0394852-3190485-2490358&"""

    print(requests.get(
      url
    ).json())

    return redirect(authorization_url)





# recieves the google server response for the login request
@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = session['state']

  flow = Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE,
      scopes=None,        state=state,
      redirect_uri=url_for('oauth2callback', _external=True)
  )



  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = request.url
  flow.fetch_token(authorization_response=authorization_response)



  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  session['credentials'] = credentials_to_dict(credentials)


  

  return redirect('/')






# middlePage to see and edit data
# determines whether to authorize or whatever
import scrape
import processData
import datetime
@app.route('/confirmData', methods=['POST', 'GET'])
def confirmData():

    # if user used get request
    if 'text' not in request.form:
        return redirect('/?e=0')

    # go back to home page if user didn't log in  yet
    if 'credentials' not in session:
      return redirect('/?e=1')

    # if the textarea input is empty
    if request.form.get('text', False) == '':
        return redirect('/?e=3')

    #json data that displays as a list on the webpage
    data = {}

    # get the start and end dates for current quarter
    map = [1, 2, 2, 2, 0, 3, 4, 0, 0, 0, 1, 1] # months => f, w, s, s1, s2
    curTime = datetime.datetime.now()
    data["year"] = str(curTime.year)
    data["quarter"] = scrape.quarters[map[int(curTime.month)-1]]
    if curTime.month >= 11:
        data["year"] = str(curTime.year+1)
    data["startDate"], data["endDate"] = scrape.get_dates(data["year"]+" "+data["quarter"])

    # load the post data (if the previous request was a post)
    listEvents = [{}]
    data["alert"] = "false"
    if request.method == 'POST':
        try:
            listEvents = processData.webreg_json(request.form.get("text", False))
        except ValueError as e:
            return redirect('/?e=2')
    data["numRows"] = len(listEvents)
    data["values"] = str(listEvents)

    # load this page with the data that we have
    return render_template("confirmData.php", data=data)






# basically a nonexistent page to process the data and put it on the calendar
@app.route('/sendData', methods=['POST'])
def sendData():

    '''a = ""
    for x in session:
        a += str(x) +": "+ str(session[x]) + "<br>"
    return a'''


    # go back to home page if user didn't log in  yet
    if 'state' not in session:
      return redirect('/?e=1')

    # back home if its a get request
    if 'numRows' not in request.form:
        return redirect("/?e=0")

    # Load credentials from the session.
    credentials = Credentials(** session['credentials'])
    cal = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    data = request.form

    # add this new subcalendar in the users calendar
    cal_name = "webregCourses"
    if data['name'] != '':
        cal_name = data['name']
    new_cal = {
        'summary': cal_name,
        'timeZone': 'America/Los_Angeles'
    }
    add = True
    page_token = None
    while add:
      calendar_list = cal.calendarList().list(pageToken=page_token).execute()
      for calendar in calendar_list['items']:
        if calendar['summary'] == new_cal['summary']:
            add = False
            new_cal = calendar
            break
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    if add:
        new_cal = cal.calendars().insert(body=new_cal).execute()
    #print(str(new_cal))

    # add the data row by row
    for i in range(int(data["numRows"])):

        row = "R"+str(i+1)  # helpful name

        # get the days that we have this class

        date =  data.get(row+"date")
        startDate = data.get("startDate")
        endDate = data.get("endDate")
        firstDay = startDate

        hi = {}

        if '/' in date:
            m, d, y = date.split("/")
            firstDay = "-".join([y, m, d])

            # if this day is not between thet ranges, next row
            #if not processData.AbeforeB(startDate, firstDay) or not processData.AbeforeB(firstDay, endDate):
            #    continue

        else:

            # this was a class that occured more than once during this period
            # get the days with holidays and the first day of class

            if not processData.AbeforeB(startDate, endDate):
                return redirect("/?e=4")

            whichDays = []
            map = ["mo", 'tu', 'we', 'th', 'fr', 'sa', 'su']
            for i in range(len(map)):
                if map[i].upper() in date:
                    whichDays.append(i)

            # monday-sunday: 0-6
            y, m, d = (int(x) for x in startDate.split("-"))
            w = datetime.date(y, m, d).weekday()

            count = 0
            holidays = []
            while True:
                today = str(y)+"-"+processData.date_to_str(m)+"-"+processData.date_to_str(d)
                if processData.isHoliday((y,m,d,w)):
                    holidays.append(today)
                elif w in whichDays:
                    count += 1
                    if count == 1:
                        firstDay = today
                if today == endDate:
                    break
                y,m,d,w = processData.next_day((y,m,d,w))

            hi['recurrence'] = [
                #'EXDATE;VALUE=DATE:'+','.join(x''.join(x.split('-')) for x in holidays ),
                'RRULE:FREQ=WEEKLY;UNTIL=' + (''.join(endDate.split('-'))) + ';BYDAY=' + date,
            ]

        # these are the same whether or not the event is recurring or not
        hi['summary'] =  data.get(row+"title"),
        hi['location'] =  data.get(row+"location"),
        hi['description'] =  data.get(row+"description"),
        hi['start'] = {
            'dateTime':  firstDay+ 'T' +  data.get(row+"startH")+":"+data.get(row+"startM")+":00",
            'timeZone': 'America/Los_Angeles',
        }
        hi['end'] = {
            'dateTime': firstDay + 'T' +  data.get(row+"endH")+":"+data.get(row+"endM")+":00",
            'timeZone': 'America/Los_Angeles',
        }

        hi = cal.events().insert(calendarId=new_cal['id'], body=hi).execute()

        # delete recurring events on holidays
        if '/' not in date:
            instances = cal.events().instances(calendarId=new_cal['id'], eventId=hi['id']).execute()['items']
            for instance in instances:
                #print(instance['start']['dateTime'].split('T')[0])
                if instance['start']['dateTime'].split('T')[0] in holidays:
                    cal.events().delete(calendarId=new_cal['id'], eventId=instance['id']).execute()

    session.clear()
    return redirect('/')



@app.route('/revoke')
def revoke():
  if 'credentials' not in session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = Credentials(**session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')

  if status_code == 200:
    session.clear()
    return('Credentials successfully revoked.')
    #return redirect("/")
  else:
    return('An error occurred.')




@app.route('/clear')
def clear_credentials():
  if 'credentials' in session:
    del session['credentials']
  return ('/')



def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



import os
if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    
    
    #not this one;os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    app.run(
      port=5000, debug=True
      , ssl_context='adhoc'
    ) 









