'''
## Pre-requisites
1. Add user credentials to Gitlab CI secret variables for Checkmarx authentication
2. Edit gitlab-ci.yml to include below config after post build in any Test stage:
    before_script:
        - pip install -r requirements.txt
    script:
        - python scan.py --repo_name=$CI_PROJECT_NAME --username=$CxUSER --password=$CxPASS
3. Include below config in gradle.build file to perform Open Source Analysis scan
    task copyDependencies(type: Copy) {
       from configurations.compile
       into 'dependencies'
    }
'''


import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--username", help="CxSAST API username to be used for scanning", required=True, type=str, nargs=1)
parser.add_argument("--password", help="CxSAST API user's password to be used for scanning", required=True, type=str,
                    nargs=1)
parser.add_argument("--repo_name", help="Project to be scanned. Here it's current repo", required=True, type=str,
                    nargs=1)
parser.add_argument("--osa", help="Perform OSA scan.", action='store_true')
args = parser.parse_args()

repo_name = args.repo_name[0]
username = args.username[0]
password = args.password[0]
osa = args.osa

r1 = requests.post('https://sca.smartthings.com/CxRestAPI/auth/login', data={"username": username, "password": password})
if r1.status_code != 200:
    print "Authentication failed: "+str(r1.text)
else:
    # Get list of all projects created previously in Checkmarx
    headers={'CXCSRFToken': r1.cookies['CXCSRFToken']}
    cookies = r1.cookies
    r2 = requests.get('https://sca.smartthings.com/CxRestAPI/projects', cookies=cookies, headers=headers)
    if r2.status_code != 200:
        print "Unable to get project list: "+str(r2.text)
    else:
        projects = json.loads(r2.text)
        projectId = ''
        for i in range(0, len(projects)):
            if projects[i]['name'] == repo_name:
                projectId = projects[i]['id']
        if projectId == '':
            print "Seems like this repo "+str(repo_name)+" has not been added to Checkmarx yet!!"
        else:
            # Initiate code scan
            data={"projectId": projectId, "isIncremental": "True", "isPublic": "False", "forceScan": "True"}
            r3 = requests.post('https://sca.smartthings.com/CxRestAPI/sast/scans', headers=headers, cookies=cookies, data=data)
            print str(r3.status_code)
            # Initiate OSA scan
            if osa == True:
                osa_url='https://sca.smartthings.com/CxRestAPI/osa/scans'
                files={'zippedSource': open('./dependencies.zip','rb')}
                values={"projectId": projectId,"origin":"API", "zippedSource":"dependencies.zip"}
                r4=requests.post(osa_url,files=files,data=values,headers=headers,cookies=r1.cookies)
                print str(r4.status_code)
