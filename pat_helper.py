"""
pat_helper
----------

Create mode:
  1. (optional) Tests to see if the LDAP username and password are currently valid
  2. Creates a personal access token (PAT) in BitBucket Server (Stash)
  3. The PAT & PAT ID is output in GitHub Actions style output

Revoke mode:
  1. (optional) Tests to see if the LDAP username and password are currently valid
  2. Revokes a personal access token (PAT) in BitBucket Server (Stash)
"""

# pylint: disable=global-statement,missing-function-docstring

import argparse
import os
import sys
import time
import urllib.parse

import requests

from ldap3 import Server, Connection, ALL

LDAP_PATH = ''
LDAP_HOSTS = []
LDAP_PORT = 389
MAX_ATTEMPTS = 10
PASSWORD = None
PAT = None
PAT_ID = None
PAT_VALID = 1  # days
STASH_HOST = ''
STASH_PAT_URI = 'rest/access-tokens/1.0/users'
USER_LDAP = None
USERNAME = None
WAIT_BETWEEN_ATTEMPTS = 30  # seconds

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['create', 'revoke'])
    parser.add_argument('--check-using-ldap-bind', choices=['true', 'false'], default='false')
    parsed = parser.parse_args()
    return parsed

def get_from_env(variable):
    if not os.environ.get(variable):
        print(f"🙈 Environment variable '{variable}' not found, but is required")
        sys.exit(255)
    return os.environ[variable]

def parse_env():
    # required
    global USERNAME
    USERNAME = get_from_env('username')
    global PASSWORD
    PASSWORD = get_from_env('password')
    global STASH_HOST
    STASH_HOST = get_from_env('base_url').rstrip('/')

    # optional
    if os.environ.get('pat_uri'):
        global STASH_PAT_URI
        STASH_PAT_URI = get_from_env('pat_uri').lstrip('/')
    if os.environ.get('max_attempts'):
        global MAX_ATTEMPTS
        MAX_ATTEMPTS = int(get_from_env('max_attempts'))
    if os.environ.get('seconds_between_attempts'):
        global WAIT_BETWEEN_ATTEMPTS
        WAIT_BETWEEN_ATTEMPTS = int(get_from_env('seconds_between_attempts'))
    if os.environ.get('valid_days'):
        global PAT_VALID
        PAT_VALID = int(get_from_env('valid_days'))


def get_pat_id():
    global PAT_ID
    PAT_ID = get_from_env('pat_id')


def get_ldap_vars():
    # required
    global LDAP_PATH
    LDAP_PATH = get_from_env('ldap_path')
    global LDAP_HOSTS
    hosts = get_from_env('ldap_hosts')
    LDAP_HOSTS = hosts.split(',')

    # optional
    if os.environ.get('ldap_port'):
        global LDAP_PORT
        LDAP_PORT = get_from_env('ldap_port')

    global USER_LDAP
    USER_LDAP = f"CN={USERNAME},{LDAP_PATH}"


def test_password(host):
    server = Server(host=host, port=LDAP_PORT, use_ssl=False, get_info=ALL)
    connection = Connection(server, user=USER_LDAP, password=PASSWORD, version=3, authentication='SIMPLE')
    for _ in range(MAX_ATTEMPTS):
        try:
            if connection.bind():
                print(f"✅ Password for user {USERNAME} is valid with {host}")
                break

            print(f"⏳ Password for user {USERNAME} not (yet) valid with {host}")
        except Exception as err:  # pylint: disable=broad-except
            print(f"💥 Exception trying username + password on {host}:\n{err}")

        if _ != max(range(MAX_ATTEMPTS)):
            print(f"⏱ Trying again in {WAIT_BETWEEN_ATTEMPTS} seconds")
            time.sleep(WAIT_BETWEEN_ATTEMPTS)
        else:
            print(f"👎 Giving up, reached maximum attempts ({MAX_ATTEMPTS})")
            sys.exit(127)


def token_name():
    name = 'local-test'
    if os.environ.get('GITHUB_REPOSITORY'):
        name = f"github-{os.environ['GITHUB_REPOSITORY']}"
    return name


def create_pat():
    data = {
        "name": token_name(),
        "permissions": [
            "REPO_WRITE",
            "PROJECT_WRITE",
        ],
        "expiryDays": PAT_VALID,
    }

    pat = None
    for _ in range(MAX_ATTEMPTS):
        pat = requests.put(f"{STASH_HOST}/{STASH_PAT_URI}/{USERNAME}", json=data, auth=(USERNAME, PASSWORD))
        if pat.status_code == 200:
            break
        if pat.status_code == 401:
            print(f"⏳ Password for user {USERNAME} not (yet) valid with {STASH_HOST}")
        else:
            print(f"⚠️ Stash returned a status that was not 200 or 401: {pat.status_code}")
            print(f"{pat.headers}")
            print(f"{pat.text}")
            sys.exit(63)

        if _ != max(range(MAX_ATTEMPTS)):
            print(f"⏱ Trying again in {WAIT_BETWEEN_ATTEMPTS} seconds")
            time.sleep(WAIT_BETWEEN_ATTEMPTS)
        else:
            print(f"👎 Giving up, reached maximum attempts ({MAX_ATTEMPTS})")
            sys.exit(127)

    try:
        pat_json = pat.json()
    except Exception as err:  # pylint: disable=broad-except
        print(f"💥 Exception trying to decode Stash response as json:\n{err}")
        sys.exit(32)

    if not pat_json.get('token'):
        print(f"🙈 Stash didn't return a token in the response:\n{pat_json}")
        sys.exit(31)
    if not pat_json.get('id'):
        print(f"🙈 Stash didn't return an id in the response:\n{pat_json}")
        sys.exit(30)

    global PAT
    PAT = pat_json['token']
    global PAT_ID
    PAT_ID = pat_json['id']

    print(f"🗝 Stash has issued PAT ID {PAT_ID} for user {USERNAME}")


def revoke_pat():
    pat = None
    for _ in range(MAX_ATTEMPTS):
        pat = requests.delete(f"{STASH_HOST}/{STASH_PAT_URI}/{USERNAME}/{PAT_ID}", auth=(USERNAME, PASSWORD))
        if pat.status_code == 204:
            break
        if pat.status_code == 401:
            print(f"⏳ Password for user {USERNAME} not (yet) valid with {STASH_HOST}")
        else:
            print(f"⚠️ Stash returned a status that was not 204 or 401: {pat.status_code}")
            print(f"{pat.headers}")
            print(f"{pat.text}")
            sys.exit(62)

        if _ != max(range(MAX_ATTEMPTS)):
            print(f"⏱ Trying again in {WAIT_BETWEEN_ATTEMPTS} seconds")
            time.sleep(WAIT_BETWEEN_ATTEMPTS)
        else:
            print(f"👎 Giving up, reached maximum attempts ({MAX_ATTEMPTS})")
            sys.exit(127)

    print(f"🗑 Revoked PAT ID {PAT_ID} for user {USERNAME}")

    global PAT
    PAT = 'revoked'


def print_outputs():
    username_encoded = urllib.parse.quote(USERNAME, safe='')
    pat_encoded = urllib.parse.quote(PAT, safe='')
    print(f"::add-mask::{PAT}")  # mark the PAT as secret in GitHub Actions logs
    print(f"::add-mask::{pat_encoded}")  # mark the PAT as secret in GitHub Actions logs
    print(f"::set-output name=username::{USERNAME}")
    print(f"::set-output name=username_encoded::{username_encoded}")
    print(f"::set-output name=pat::{PAT}")
    print(f"::set-output name=pat_encoded::{pat_encoded}")
    print(f"::set-output name=pat_id::{PAT_ID}")

    # STATE_CLEANUP_PAT_ID will be used in the post action phase to automatically revoke the PAT
    print(f"::save-state name=CLEANUP_PAT_ID::{PAT_ID}")

##==--------------------------------------------------------------------
##  Main...


args = parse_args()
parse_env()
if args.mode == 'revoke':
    get_pat_id()

if args.check_using_ldap_bind == 'true':
    get_ldap_vars()
    for ldap_host in LDAP_HOSTS:
        test_password(ldap_host)

if args.mode == 'create':
    create_pat()
else:  # revoke
    revoke_pat()

print_outputs()
