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

# ============================
# Environment vars part 
# ============================

mypassword = os.environ.get("ICPSR_PASS")
mylogin = os.environ.get("ICPSR_EMAIL")
debug = os.environ.get("DEBUG")
savepath = "."

# get pid from config file:

try:
    with open('config.yml') as f:
        config = next(yaml.load_all(f, Loader=yaml.FullLoader))
        pid=config['openicpsr']
except FileNotFoundError:
    print('No config file found')

# ============================

headers = {
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.icpsr.umich.edu",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": None,
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/102.0.0.0 Safari/537.36"
    ),
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "sec-gpc": "1",
}

oheaders = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Referer": "https://www.openicpsr.org/openicpsr/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-gpc": "1",
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


# here we check if the directory already exists.
# If it does, then we don't do anything.

if os.path.exists(pid):
    print(f"Directory already exists, doing nothing")
    quit()

if len(mypassword) == 0:
        print(f"Password must be passed via ENV")
        print(f"or by specifying a login as arg3, then prompt for password")
        exit()

if debug == 1:
    print(len(sys.argv))
    print(str(sys.argv))

with requests.Session() as session:
    # Get required session cookies
    req = session.get(
        "https://www.icpsr.umich.edu/mydata?path=ICPSR",
        headers=headers,
        allow_redirects=True,
    )
    req.raise_for_status()
    cookies = req.cookies

    headers.update(
        {
            "Origin": "https://www.icpsr.umich.edu",
            "Referer": "https://www.icpsr.umich.edu/rpxlogin",
        }
    )
    login_req = session.post(
        "https://www.icpsr.umich.edu/rpxlogin",
        headers=headers,
        cookies=cookies,
        files={
            "email": (None, mylogin),
            "password": (None, mypassword),
            "path": (None, "ICPSR"),
            "request_uri": (None, "https://www.icpsr.umich.edu/mydata?path=ICPSR"),
            "noautoguest": (None, ""),
            "Log In": (None, "Log In"),
        },
    )
    login_req.raise_for_status()
    cookies.update(login_req.cookies)
    req = session.get(
        "https://www.icpsr.umich.edu/mydata?path=ICPSR",
        headers=headers,
        cookies=cookies,
        allow_redirects=True,
    )
    req.raise_for_status()

    # OAUTH FLOW OpenICPSR <-> ICPSR
    r = session.get("https://www.openicpsr.org/")
    r.raise_for_status()
    cookies.update(r.cookies)  # get JSESSIONID

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
    except AttributeError:
        print("Wrong user / password!!!")
        exit()
    resp = session.get(callback_url, headers=oheaders, cookies=cookies, stream=True)
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
