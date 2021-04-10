import json
import urllib.request
import os
from datetime import datetime
from collections import defaultdict
import calendar
import sys
import re
import boto3
from botocore.exceptions import ClientError



def send_email(the_sender, the_recipient, the_subject, the_body_html):

    SENDER = the_sender
    RECIPIENT = ", ".join(the_recipient)
    AWS_REGION = "us-west-2"
    SUBJECT = the_subject
    BODY_HTML = the_body_html
    CHARSET = "UTF-8"

    client = boto3.client('ses',region_name=AWS_REGION)
    
    
    try:
        response = client.send_email(
        Destination={'ToAddresses': the_recipient},
        Message={'Body': {'Html': {'Charset': CHARSET,'Data': BODY_HTML,},},'Subject': {'Charset': CHARSET,'Data': SUBJECT,},},
        Source=SENDER,
        )

    except ClientError:
        print(e.response['Error']['Message'])
    else:
        print("Ok!")


def xstr(s):
    if s is None:
        return ''
    return str(s)
    

def get_movie_data(x_days, x_zip):
    
    show_day=datetime.today().strftime('%Y-%m-%d')
    
    api_key = os.environ['api_key']
    
    
    movie_url = 'http://data.tmsapi.com/v1.1/movies/showings?startDate=' + show_day + '&numDays=' + x_days + '&zip=' + x_zip + '&api_key=' + api_key
    
    try:
        movie_json = json.load(urllib.request.urlopen(movie_url))
    except urllib.request.HTTPError:
        exit(1)
    
    
    movie_list=[]
    
    for r in movie_json:
           for ii in r['showtimes']:
                dirs = r.get('directors', '?')
                director_str = ' '.join(map(str, dirs))
                movie_list.append([str(ii['theatre']['name']).strip(), str(ii['dateTime']).strip(), str(r['title']).strip()  +  ' (Dir: ' + director_str + ')' ])

                
    html_output=''
    
    d = defaultdict(set)
    
    
    for i in movie_list:
        try:
            d[i[0]].add(i[2])
        except KeyError:
            d[i[0]] = i[2]
    
    
    for key, value in sorted(d.items()):
    	html_output += '<u><b>' + key + '</b></u>'
    	for x in value:
    		html_output += '<br>' + x
    	html_output += '<br><br>'
    
    
    return html_output



def lambda_handler(event, context):
    days = event["days"]
    zipcode = event["zipcode"]
    send_to = event["recipients"]

    subject_line='Movies Playing in San Francisco'
    
    movie_msg=get_movie_data(days, zipcode)
    send_email("Movie Phoney <wilsonswobbler@gmail.com>",send_to , subject_line, movie_msg)
    


