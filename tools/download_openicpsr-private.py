#!/usr/bin/python3
# Tool to download from unpublished (private) openICPSR deposit
# Provided by Kacper Kowalik (xarthisius)
import functools
import re
import requests
import os
import sys
import getpass
import yaml
import zipfile
from urllib.parse import parse_qs, urlparse

# ============================
# Environment vars part 
# ============================
OPENICPSR_URL = "https://www.openicpsr.org/openicpsr/workspace"
mypassword = os.environ.get("ICPSR_PASS")
mylogin = os.environ.get("ICPSR_EMAIL")
debug = os.environ.get("DEBUG")
savepath = "."

if debug :
    print("Debug turned on")
else:
    print("No debug:" + str(debug))
# get pid from config file:

try:
    with open('config.yml') as f:
        config = next(yaml.load_all(f, Loader=yaml.FullLoader))
        pid=config['openicpsr']
except FileNotFoundError:
    print('No config file found')

# ============================

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}


try:
    # parse command line overrides
    if len(sys.argv) >= 2:
        pid = sys.argv[1]
    if len(sys.argv) >= 3:
        savepath = sys.argv[2]
    if len(sys.argv) >= 4:
        mylogin = sys.argv[3]
        # if we are provided a login, we prompt for the password
        print(f"===========================================")
        print(f"Project ID: {pid}")
        print(f"Path      : {savepath}")
        print(f"Login     : {mylogin}")
        mypassword = getpass.getpass()
except IndexError:
    print(f"Usage: {__name__} <PROJECT ID> [path] [login]")
    exit()



if len(mypassword) == 0:
        print(f"Password must be passed via ENV")
        print(f"or by specifying a login as arg3, then prompt for password")
        exit()

if debug == 1:
    print(len(sys.argv))
    print(str(sys.argv))

with requests.Session() as session:
    # Get required session cookies
    print("Getting session cookies...")
    req = session.get(
        OPENICPSR_URL,
        headers=headers,
    )
    req.raise_for_status()
    cookies = req.cookies  # Get JSESSIONID

    print("Initiating OAuth flow...")
    headers["Referer"] = OPENICPSR_URL
    login_req = session.get(
        f"{OPENICPSR_URL}/login",    
        headers=headers,
        cookies=cookies,
        allow_redirects=True,
    )
    login_req.raise_for_status()

    action_url_pattern = r'action="([^"]*)"'
    matches = re.findall(action_url_pattern, login_req.text)
    action_url = matches[0] if matches else None

    # Parse the URL to extract query parameters
    url_components = urlparse(action_url.replace("&amp;", "&"))
    query_params = parse_qs(url_components.query)

    # Extract specific decoded query parameters
    params = {
        param: query_params.get(param)[0]
        for param in ["session_code", "client_id", "execution", "tab_id"]
    }

    data = {
        "username": mylogin,
        "password": mypassword,
    }
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    print("Logging in...")
    req = session.post(
        "https://login.icpsr.umich.edu/realms/icpsr/login-actions/authenticate",
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        allow_redirects=True,
    )
    req.raise_for_status()
    headers.pop("Content-Type")


    data_url = (
        f"https://deposit.icpsr.umich.edu/deposit/downloadZip?dirPath=/openicpsr/{pid}"
    )
    data_req = session.get(data_url, headers=oheaders, cookies=cookies)
    data_req.raise_for_status()
    oauth_redir_url = data_req.headers.get("Refresh").split("URL=")[-1]
    oauth_redir_req = session.get(oauth_redir_url, headers=oheaders, cookies=cookies)
    oauth_redir_req.raise_for_status()

    try:
        callback_url = oauth_redir_req.headers.get("Refresh").split("URL=")[-1]
        if debug:
            print("callback_url: " + callback_url)
    except AttributeError:
        print("Wrong user / password!!!")
        exit()
    resp = session.get(callback_url, headers=oheaders, cookies=cookies, stream=True)
    resp.raise_for_status()
    
    if resp.headers.get("Content-Encoding") in ("gzip",):
        resp.raw.read = functools.partial(resp.raw.read, decode_content=True)

    fname = re.findall("filename=(.+)", resp.headers["Content-Disposition"])[0].strip('"')
    outfile=f"{savepath}/{fname}"
    with open(f"{savepath}/{fname}", "wb") as fp:
        for chunk in resp.raw:
            fp.write(chunk)

# in principle, we should now have a file

try:
    with zipfile.ZipFile(outfile) as z:
        print('File downloaded '+outfile)
        # here we check if the directory already exists.
        # If it does, then we don't do anything.
        if os.path.exists(pid):
            print(f"Directory already exists, doing nothing")
            quit()
        # if it does not, we extract in the standard path
        z.extractall(path=str(pid))
except FileNotFoundError:
    print('No downloaded file found')
    print('Something went wrong')
    quit()

# Now git add the directory, if we are in CI

if os.getenv("CI"):
    # we are on a pipeline/action
    os.system("git add "+str(pid))
    os.system("git commit -m '[skip ci] Adding files from openICPSR project "+str(pid)+"' "+str(pid))
else:
    print("You may want to 'git add' the contents of "+str(pid))
