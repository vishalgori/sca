import os
import requests
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_repos(url, token):
    res = requests.get(url, headers={"Authorization": token})
    repos = res.json()
    while 'next' in res.links.keys():
        res = requests.get(res.links['next']['url'], headers={"Authorization": token})
        repos.extend(res.json())
    return repos


def create_cxsast_projects(repos, cx_url, cx_user, cx_pass, cx_team_id, git_user, git_pass):
    # SSL verification is set to false since we are using a self signed certificate behind the load balancer on the server.
    requests.packages.urllib3.disable_warnings()
    r1 = requests.post(cx_url + 'auth/login',
                       data={"username": cx_user, "password": cx_pass}, verify=False)
    for i in range(0, len(repos)):
        project_name = repos[i]['name']
        source_url = 'https://' + git_user + ':' + git_pass + '@' + repos[i]['git_url'].split('//')[1]
        r2 = requests.post(cx_url + '/projects', cookies=r1.cookies,
                           headers={'CXCSRFToken': r1.cookies['CXCSRFToken']},
                           data={"name": project_name, "owningTeam": cx_team_id,
                                 "isPublic": True}, verify=False)
        if r2.status_code == 201:
            logger.info("Project created. Adding source control")
            r3 = requests.post(cx_url + '/projects/' + str(r2.json()['id']) + '/sourceCode/remoteSettings/git',
                               cookies=r1.cookies,
                               headers={'CXCSRFToken': r1.cookies['CXCSRFToken']},
                               data={"url": source_url, "branch": "refs/heads/master"}, verify=False)
            if r3.status_code != 204:
                logger.info("Couldn't add source control for: %s", project_name,
                            " still continuing adding other projects.")
                continue
        elif r2.json()["messageCode"] == 12108:
            logger.info('%s,%s', r2.json()["messageDetails"], project_name)
            continue
        else:
            logger.info("Unexpected error: %s,%s", r2.status_code, project_name)


def main(event, context):
    # Getting secrets from AWS Secrets Manager first
    secret_name = "setup_github_sca"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("The requested secret %s" + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logger.info("The request was invalid due to:%s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logger.info("The request had invalid params:%s", e)
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']

    git_token = "token " + secret['git_token']  # Github API Token
    git_user = secret['github_user']  # SCA Github user
    git_pass = secret['github_pass']  # SCA Github user's password
    cx_user = secret['cx_user']  # Checkmarx SCA user
    cx_pass = secret['cx_pass']  # Checkmarx SCA user's password
    git_url = os.environ['git_url']  # https://api.github.com/orgs/{org-name}/repos?simple=yes&per_page=100&page=1
    cx_url = os.environ['cx_url']  # https://cx_url/CxRestAPI/
    cx_team_id = os.environ['cx_team_id']  # Checkmarx team ID to create projects under
    repos = get_repos(git_url, git_token)
    create_cxsast_projects(repos, cx_url, cx_user, cx_pass, cx_team_id, git_user, git_pass)
