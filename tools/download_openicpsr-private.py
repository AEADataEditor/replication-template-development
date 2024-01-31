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
OPENICPSR_URL = "https://www.openicpsr.org/openicpsr/"
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

    print("Accessing files...")
    data_url = (
        f"https://deposit.icpsr.umich.edu/deposit/downloadZip?dirPath=/openicpsr/{pid}"
    )

    print("Getting file info...")
    head_response = session.head(data_url, headers=headers, cookies=cookies)
    head_response.raise_for_status()
    # Get the filename from the Content-Disposition header
    filename = re.findall("filename=(.+)", head_response.headers["Content-Disposition"])[0].strip('"')
    outfile=f"{savepath}/{filename}"

    if filename:
        print(f"Downloading file: {filename}")

        # Send a GET request with stream=True to download the ZIP file
        get_response = session.get(data_url, headers=head_response.headers, stream=True)

        # Check if the GET request was successful (status code 200)
        if get_response.status_code == 200:
            # Create a ZipFile object from the content of the response
            with open(f"{outfile}", "wb") as fp:
                for chunk in get_response.raw:
                    fp.write(chunk)
        else:
            print(
                f"Failed to download ZIP file. Status code: {get_response.status_code}"
            )
    else:
        print("Filename not found in Content-Disposition header.")


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
