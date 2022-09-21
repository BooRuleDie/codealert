import urllib3
import requests
import json
import sqlite3
import hashlib
import os
from getpass import getuser
from colorama import Fore, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def checkQuery(MD5HASH):   
    connection = sqlite3.connect("database.db")
    with connection as conn:
        cursor = conn.cursor()
        results = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        
        tables = []
        for result in results.fetchall():
            tables.append(result[0])

        if MD5HASH not in tables:
            return True
    return False       
    
def getJSON(search, GITHUB_API, md5hash):   
    if checkQuery(md5hash):
        url = "https://api.github.com/search/code"
        params = {
            "q" : search
        }  
        headers = {
            "Accept" : "application/vnd.github+json",
            "Authorization" : f"Bearer {GITHUB_API}"
        }

        r = requests.get(url=url, headers=headers, params=params, verify=False)
        JSON = json.loads(r.text)
        
        return JSON
    print(f"{Style.RESET_ALL}[{Fore.RED}!{Fore.RESET}] You've already added this cronjob.")
    print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
    exit()
    
def writeToDb(items, MD5HASH):
    
    connection = sqlite3.connect("database.db")
    with connection as conn:
        cursor = conn.cursor()

        # create the hash table
        cursor.execute(f"create table '{MD5HASH}' (name TEXT)")

        for file in items:
            cursor.execute(f"""insert into '{MD5HASH}' values('{file["html_url"]}')""")
            print(f'{counter}: {file["html_url"]}')
        
        conn.commit()

def initiateCronjob(query, MD5HASH):
    currentDir = os.getcwd()
    username = getuser()
    
    # check if Scripts Directory exists
    if not os.path.exists("Scripts"):
        os.makedirs("Scripts")
    
    script = open("script.txt").read()

    someVars = f"""\
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
MD5HASH = "{MD5HASH}"
QUERY = "{query}"

"""
    script = someVars + script

    # create scripts
    with open(f"Scripts/{MD5HASH}.py", "w") as f:
        f.write(script)

    # change reexecution time
    os.system(f"""(crontab -l 2>/dev/null ; echo "0 8 * * * cd {currentDir}/Scripts && /usr/bin/python3 {currentDir}/Scripts/{MD5HASH}.py") | crontab -u {username} -""")
    print(f"[{Fore.GREEN}+{Fore.RESET}] {Style.BRIGHT}New cronjob has been successfully added!{Style.RESET_ALL}")

def printbanner():
    banner = f"""\
{Fore.RED}┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{Fore.RESET}
{Fore.RED}┃{Fore.RESET}{Style.BRIGHT}    ______          __     ___    __          __  {Style.RESET_ALL}{Fore.RED}┃{Fore.RESET} 
{Fore.RED}┃{Fore.RESET}{Style.BRIGHT}   / ____/___  ____/ /__  /   |  / /__  _____/ /_ {Style.RESET_ALL}{Fore.RED}┃{Fore.RESET} 
{Fore.RED}┃{Fore.RESET}{Style.BRIGHT}  / /   / __ \/ __  / _ \/ /| | / / _ \/ ___/ __/ {Style.RESET_ALL}{Fore.RED}┃{Fore.RESET} 
{Fore.RED}┃{Fore.RESET}{Style.BRIGHT} / /___/ /_/ / /_/ /  __/ ___ |/ /  __/ /  / /_   {Style.RESET_ALL}{Fore.RED}┃{Fore.RESET} 
{Fore.RED}┃{Fore.RESET}{Style.BRIGHT} \____/\____/\__,_/\___/_/  |_/_/\___/_/   \__/   {Style.RESET_ALL}{Fore.RED}┃{Fore.RESET} 
{Fore.RED}┃{Fore.RESET}                                                  {Fore.RED}┃{Fore.RESET} 
{Fore.RED}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Fore.RESET} 
                                    {Fore.RED}By BooRuleDie{Fore.RESET}
                                        
[{Fore.BLUE}?{Style.RESET_ALL}] {Fore.BLUE}Please enter your dork \033[33;5m>\033[0m {Fore.YELLOW}"""

    os.system("clear")
    dork = input(banner)
    return dork

def main():
    try:
        search = printbanner()
        print()
        query2string = "".join(sorted(search.split()))
        md5hash = hashlib.md5(query2string.encode()).hexdigest()

        JSON_CONF = json.load(open("confidential.json"))
        GITHUB_API = JSON_CONF["Github-API"]

        JSON = getJSON(search, GITHUB_API, md5hash)

        if JSON["total_count"] == 0:
            print(f"{Style.RESET_ALL}[{Fore.RED}-{Style.RESET_ALL}] {Style.BRIGHT}Couldn't find any file.{Style.RESET_ALL}")
            print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
        else:
            answer = input(f"{Style.RESET_ALL}[{Fore.GREEN}+{Fore.RESET}] {Style.BRIGHT}{Fore.GREEN}{JSON['total_count']}{Style.RESET_ALL} files found, do you want to proceed ? (y/n) ")

            if answer.upper() == "Y" or answer.upper() =="YES":    
                writeToDb(JSON["items"], md5hash)
                initiateCronjob(search, md5hash)
            else:
                print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
    except:
        print(f"{Style.RESET_ALL}[{Fore.RED}-{Fore.RESET}] {Style.BRIGHT}Something went wrong! {Style.RESET_ALL}")
        print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()