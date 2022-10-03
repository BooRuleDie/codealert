# What is codealert ?

It's a tool to track some github dorks' results. 

![tool's interface image](https://i.imgur.com/RfFYEz9.png)

### Here is how it works:

**1.** User issues a GitHub dork to the tool.
    <p style="margin-left: 25px"><img src="https://i.imgur.com/UF4JZ9K.png" alt="step 1" width="300"/></p>

**2.** The tool creates a cronjob that'll run a script that checks this dork every day *(2 am)*.
    <p style="margin-left: 25px"><img src="https://i.imgur.com/xGrVvfF.png" alt="step 1" width="300"/></p>

**3.** Then the tool notify you with a mail when it detects a new file that matches with your dork.
    <p style="margin-left: 25px"><img src="https://i.imgur.com/CbRuHJJ.png" alt="step 1" width="300"/></p>

---

# Installation

I've already prepared a file named **prepare.sh** to install all dependencies and software like PostgreSQL. However, it's important to note that the tool was made to run on **Ubuntu 20.04** so if you're using any other OS, it might not work.

### confidentail.json

It's a JSON file that you need to specify the needed credentials for the tool to work.

<p style="text-align:center"><img src="https://i.imgur.com/0aRi6ac.png" alt="step 1" width="300"/></p>

* **Github-API**: You need to specify a GitHub **PAT**(Personal Access Token). In order to get one:
  
  - Sign up an account on github.com.
  - At the home page, click your profile photo at the top right corner and click **Settings**.
  - Then click **Developer settings** at the left bottom corner.
  - Select **Personal access tokens** and click **Generate new token**.
  - When you get to the authorisation page, just go to the very bottom page and create the key. Do not give that key any authorization.
  - Now you're done, copy the PAT and paste it into **condidential.json**.

After giving one PAT, the tool is ready to go, but it'd be too slow to go with just one PAT, so what I recommend is to at least add five PATs.

Also there is no limit for PAT number, so you can continue like so:
```json
{
    "Github-API1" : "ghp_1",
    "Github-API2" : "ghp_2",
    "Github-API3" : "ghp_3",
    "Github-API4" : "ghp_4",
    "Github-API5" : "ghp_5",
    "Github-API6" : "ghp_6",
    "Github-API7" : "ghp_7",
    "Google-App-Pass" : "GoogleAppPass",
    "Email-From" : "fromThis@Gmail.Email",
    "Email-To" : "toThis@Whatever.Email" 
}
```

* **Google-App-Pass**: This tool uses google mails to notify users, so you need to get a **Google-App-Pass** for a gmail email from [here](https://myaccount.google.com/apppasswords). Get it and paste it into **Google-App-Pass**.

* **Email-From**: This must be the email address that you got Google-App-Pass from.

* **Email-To**: Any email address that you want to send the notificaitons.

### PostgreSQL

The tool also uses PostgreSQL to create a queue of cronjobs so they don't use the PATs at the same time and don't get caught by GitHub's rate limit.

Just enter following commands in your command line to set PostgreSQL up.
```bash
sudo -i -u postgres
psql
create user codealert WITH PASSWORD 'codealert';
CREATE DATABASE codealert_db;
\c codealert_db
create table queue_2 (hash TEXT);
exit
exit
```

Now the tool should be ready to go :)