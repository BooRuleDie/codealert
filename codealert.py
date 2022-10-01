import urllib3
import requests
import json
import sqlite3
import hashlib
import os
from getpass import getuser
from colorama import Fore, Style
from time import sleep, time
from math import ceil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def checkQuery(MD5HASH):   
    files = os.popen("ls Databases").read().split()
    if f"{MD5HASH}.db" not in files:
        return True
    return False
    
    # connection = sqlite3.connect("database.db")
    # with connection as conn:
    #     cursor = conn.cursor()
    #     results = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        
    #     tables = []
    #     for result in results.fetchall():
    #         tables.append(result[0])

    #     if MD5HASH not in tables:
    #         return True
    # return False       
    
def fetchItems(search, GITHUB_APIs,itemNumber):   
    
    allItems = set()
    pageNumber = ceil(itemNumber/100)
    GITHUB_API_index = 0

    while(len(allItems) != itemNumber):
        for page in range(1,pageNumber+1):
            JSON = []
            
            while(len(JSON) != 100 and not ((itemNumber % 100) == len(JSON) and page == pageNumber)):
                r = requests.get(url="https://api.github.com/search/code", params={"q" : search,"page" : page,"per_page":100},headers = {"Accept" : "application/vnd.github+json","Authorization" : f"Bearer {GITHUB_APIs[GITHUB_API_index]}"})
                
                # changing github API Key in each request
                if GITHUB_API_index == len(GITHUB_APIs) - 1:
                    GITHUB_API_index = 0
                else:
                    GITHUB_API_index += 1

                try:
                    JSON = json.loads(r.text)["items"]
                    for repo in JSON:
                        allItems.add(repo["html_url"])                   
                except:
                    now = time()
                    resetDate = int(r.headers["X-Ratelimit-Reset"])

                    sleep((resetDate - now) + 4)

            #progress bar
            print(f"\r{Style.BRIGHT}[{Fore.RED}!{Fore.RESET}] {Fore.GREEN}{'#####'*page}{Fore.RED}{'-----'*(pageNumber-page)}{Fore.RESET} [{Fore.RED}!{Fore.RESET}] {int(page/(pageNumber)*100)}%", end="")

    return allItems

def writeToDb(items, MD5HASH):
    
    connection = sqlite3.connect(f"Databases/{MD5HASH}.db")
    with connection as conn:
        cursor = conn.cursor()

        # create the hash table
        cursor.execute(f"create table '{MD5HASH}' (name TEXT)")

        for file in items:
            cursor.execute(f"""insert into '{MD5HASH}' values('{file}')""")
        
        conn.commit()

def initiateCronjob(query, MD5HASH,total_count):
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
from math import ceil
from time import time, sleep

JSON = json.load(open("../confidential.json"))

GITHUB_APIs = [JSON["Github-API1"],JSON["Github-API2"],JSON["Github-API3"],JSON["Github-API4"],JSON["Github-API5"]]
EMAIL_ADDRESS = JSON["Email-From"]
EMAIL_PASSWORD = JSON["Google-App-Pass"]
EMAIL_TO = JSON["Email-To"]
MD5HASH = "{MD5HASH}"
QUERY = "{query}"
TOTAL_COUNT = "{total_count}"
"""
    script = someVars + script

    # create scripts
    with open(f"Scripts/{MD5HASH}.py", "w") as f:
        f.write(script)

    # change reexecution time
    os.system(f"""(crontab -l 2>/dev/null ; echo "* * * * * cd {currentDir}/Scripts && /usr/bin/python3 {currentDir}/Scripts/{MD5HASH}.py") | crontab -u {username} -""")
    print(f"\n[{Fore.GREEN}+{Fore.RESET}] {Style.BRIGHT}New cronjob has been successfully added!{Style.RESET_ALL}")

def printbanner():
    banner = f"""\
{Style.BRIGHT}{Fore.RED}+--------------------------------------------------+{Fore.RESET}
{Fore.RED}|{Fore.RESET}    ______          __     ___    __          __  {Fore.RED}|{Fore.RESET} 
{Fore.RED}|{Fore.RESET}   / ____/___  ____/ /__  /   |  / /__  _____/ /_ {Fore.RED}|{Fore.RESET} 
{Fore.RED}|{Fore.RESET}  / /   / __ \/ __  / _ \/ /| | / / _ \/ ___/ __/ {Fore.RED}|{Fore.RESET} 
{Fore.RED}|{Fore.RESET} / /___/ /_/ / /_/ /  __/ ___ |/ /  __/ /  / /_   {Fore.RED}|{Fore.RESET} 
{Fore.RED}|{Fore.RESET} \____/\____/\____/\___/_/  |_/_/\___/_/   \__/   {Fore.RED}|{Fore.RESET} 
{Fore.RED}|{Fore.RESET}                                                  {Fore.RED}|{Fore.RESET} 
{Fore.RED}+--------------------------------------------------+{Fore.RESET} 
                                    {Fore.RED}By BooRuleDie{Fore.RESET}{Style.RESET_ALL}
                                        
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
        GITHUB_APIs = [JSON_CONF["Github-API1"],JSON_CONF["Github-API2"],JSON_CONF["Github-API3"],JSON_CONF["Github-API4"],JSON_CONF["Github-API5"]]

        if not checkQuery(md5hash):
            print(f"{Style.RESET_ALL}[{Fore.RED}!{Fore.RESET}] You've already added this cronjob.")
            print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
            exit()

        r = requests.get(url="https://api.github.com/search/code", params={"q" : search,"per_page" : 1},headers = {"Accept" : "application/vnd.github+json","Authorization" : f"Bearer {GITHUB_APIs[0]}"})
        total_count = json.loads(r.text)["total_count"]

        if total_count == 0:
            print(f"{Style.RESET_ALL}[{Fore.RED}-{Style.RESET_ALL}] {Style.BRIGHT}Couldn't find any file.{Style.RESET_ALL}")
            print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
        else:
            answer = input(f"{Style.RESET_ALL}[{Fore.GREEN}+{Fore.RESET}] {Style.BRIGHT}{Fore.GREEN}{total_count}{Style.RESET_ALL} files found\n[{Fore.BLUE}?{Fore.RESET}] Do you want to proceed ? (y/n) ")
            print()

            if answer.upper() == "Y" or answer.upper() =="YES":   
                items = fetchItems(search, GITHUB_APIs, total_count)
                writeToDb(items, md5hash)
                initiateCronjob(search, md5hash, total_count)
            else:
                print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
    except KeyError:
        print(f"{Style.RESET_ALL}[{Fore.RED}-{Fore.RESET}] {Style.BRIGHT}Something went wrong! {Style.RESET_ALL}")
        print(f"[{Fore.RED}-{Style.RESET_ALL}] {Style.BRIGHT}Credentials are wrong or you have exceeded the rate limit{Style.RESET_ALL}")
        print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"{Style.RESET_ALL}[{Fore.RED}!{Style.RESET_ALL}] {Style.BRIGHT}CTRL+C detected!{Style.RESET_ALL}")
        print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")
    
    except UnicodeDecodeError:
        print(f"{Style.RESET_ALL}[{Fore.RED}-{Fore.RESET}] {Style.BRIGHT}Please try again later! {Style.RESET_ALL}")
        print(f"[{Fore.RED}!{Style.RESET_ALL}] {Fore.RED}Exiting...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()