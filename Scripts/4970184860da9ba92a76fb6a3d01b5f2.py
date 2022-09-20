import requests
import urllib3
import json
import sqlite3
import smtplib
from email.message import EmailMessage

JSON = json.load(open("../confidential.json"))

GITHUB_API = JSON["Github-API"]
EMAIL_ADDRESS = JSON["Email-From"]
EMAIL_PASSWORD = JSON["Google-App-Pass"]
EMAIL_TO = JSON["Email-To"]
MD5HASH = "4970184860da9ba92a76fb6a3d01b5f2"
QUERY = "trendyol.com api_key"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sendMail(query, files):
    msg = EmailMessage()
    msg['Subject'] = 'New Dorks Have Been Detected !'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO

    bullethtml = ""
    for file in files:
        bullethtml += f"<li><a href={file}>Click Me</li>\n" 

    html = f""""<!DOCTYPE html>
    <html>
        <body>
            <h2 style="color:rgb(19, 46, 72);">Dork: {query}</h2>
            <h2 style="color:rgb(19, 46, 72);">New Findings:</h2> 
                <ul>
                    {bullethtml}
                </ul> 
        </body>
    </html>"""

    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def updateDB(newEntries):
    
    connection = sqlite3.connect("../database.db")
    with connection as conn:
        cursor = conn.cursor()
        
        for entry in newEntries:    
            cursor.execute(f"insert into '{MD5HASH}' values('{entry}')")
            
        conn.commit()

SETAPI = set()
SETDB = set()

url = "https://api.github.com/search/code"
params = {
    "q" : QUERY
}

headers = {
    "Accept" : "application/vnd.github+json",
    "Authorization" : f"Bearer {GITHUB_API}"
}

r = requests.get(url=url, headers=headers, params=params, verify=False)
JSON = json.loads(r.text)

for file in JSON["items"]:
    SETAPI.add(file["html_url"])

connection = sqlite3.connect("../database.db")
with connection as conn:
    cursor = conn.cursor()
    
    results = cursor.execute(f"select * from '{MD5HASH}'")
    results = results.fetchall()
    
    for result in results:
        SETDB.add(result[0])

newCodes = SETAPI.difference(SETDB)

if newCodes:
    sendMail(QUERY, newCodes)
    updateDB(newCodes)
