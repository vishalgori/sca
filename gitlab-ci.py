import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--username", help="CxSAST API username to be used for scanning", required=True, type=str, nargs=1)
parser.add_argument("--password", help="CxSAST API user's password to be used for scanning", required=True, type=str,
                    nargs=1)
parser.add_argument("--repo_name", help="Project to be scanned. Here it's current repo", required=True, type=str,
                    nargs=1)
args = parser.parse_args()

repo_name = args.repo_name[0]
username = args.username[0]
password = args.password[0]

r1 = requests.post('https://sca.smartthings.com/CxRestAPI/auth/login',
                   data={"username": username, "password": password})

# To get list of all projects
r3 = requests.get('https://sca.smartthings.com/CxRestAPI/projects', cookies=r1.cookies,
                  headers={'CXCSRFToken': r1.cookies['CXCSRFToken']})
projects = json.loads(r3.text)
for i in range(0, len(projects)):
    if projects[i]['name'] == repo_name:
        projectId = projects[i]['id']
# To initiate scan
r2 = requests.post('https://sca.smartthings.com/CxRestAPI/sast/scans',
                   headers={'CXCSRFToken': r1.cookies['CXCSRFToken']}, cookies=r1.cookies,
                   data={"projectId": projectId, "isIncremental": "True", "isPublic": "False", "forceScan": "True"})
