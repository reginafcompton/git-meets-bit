import requests
from collections import defaultdict

from flask import request
from flask import jsonify, redirect, url_for
from flask import Flask

from config import HEADERS_GITHUB, BASE_URL_GITHUB, GITHUB_ACCESS_TOKEN_URL
from utils import calculate_repo_counts, calculate_total_commits, calculate_language_count, calculate_topic_count, values_from_all_pages

app = Flask(__name__)

# users/githubusername-bitbucketusername
@app.route('/api/v1/users/<usernames>', methods=['GET'])
def user_detail_view(username):
    git_username, bit_username = usernames.replace('-', ' ').split(' ')

    data = create_github_profile(git_username=git_username,
                               bit_username=bit_username)

    return jsonify(r.json())

# users?bitbucket=reginacomp&github=reginafcompton
@app.route('/api/v1/users', methods=['GET'])
def users_view():
    git_username = request.args.get('github', '')
    bit_username = request.args.get('bitbucket', '')

    # data = create_github_profile(git_username)
    data = create_bitbucket_profile(bit_username)

    return jsonify(data)


def create_github_profile(git_username):
    base_url_github = BASE_URL_GITHUB + git_username
    profile_data = {}
    
    # Get all repo data
    url = base_url_github + '/repos' + GITHUB_ACCESS_TOKEN_URL
    repos_as_json = requests.get(url, headers=HEADERS_GITHUB).json()

    # Total number of public repos
    profile_data['total_public_repos'] = calculate_repo_counts(repos_as_json)

    # Followers
    url = base_url_github + '/followers' + GITHUB_ACCESS_TOKEN_URL 
    resp = requests.get(url, headers=HEADERS_GITHUB)
    profile_data['follower_count'] = len(resp.json())

    # Stars given
    url = base_url_github + '/starred' + GITHUB_ACCESS_TOKEN_URL
    resp = requests.get(url, headers=HEADERS_GITHUB)
    profile_data['stars_given_count'] = len(resp.json())

    # Stars received 
    stargazers_count = sum([data['stargazers_count'] for data in repos_as_json])
    profile_data['stargazers_count'] = stargazers_count

    # Open issues
    open_issues_count = sum([data['open_issues_count'] for data in repos_as_json])
    profile_data['open_issues_count'] = open_issues_count

    # Total commits
    profile_data['total_commits'] = calculate_total_commits(repos_as_json)

    # Account size
    account_size = sum([data['size'] for data in repos_as_json])
    profile_data['account_size'] = account_size

    # Languages
    profile_data['language_count'] = calculate_language_count(repos_as_json)
    
    # Topics 
    profile_data['topic_count'] = calculate_topic_count(repos_as_json)

    return profile_data

def create_bitbucket_profile(bit_username):
    # Concept of stars and topics does not apply to Bitbucket
    base_url_bitbucket = "https://api.bitbucket.org/2.0/{endpoint}/{username}"
    profile_data = {}
    
    # Get all repo data
    repos_url = base_url_bitbucket.format(endpoint='repositories', username=bit_username)
    repositories = values_from_all_pages(repos_url)

    # Total number of public repos
    # TODO: original vs. forked
    profile_data['total_public_repos'] = len(repositories)

    # Followers
    followers_url = base_url_bitbucket.format(endpoint='users', username=bit_username) + '/followers'
    followers = values_from_all_pages(followers_url)
    profile_data['follower_count'] = len(followers)

    account_size = 0
    language_count = defaultdict(int)
    total_commits = 0 
    total_issues = 0
    for data in repositories:
        account_size += data['size']
        
        if data['language']:
            language_count[data['language']] += 1

        # Total commits
        if not data.get('parent'):
            commits_url = data['links']['commits']['href']
            commits = values_from_all_pages(commits_url)
            total_commits += len(commits)

        # Total open issues
        if data['has_issues'] == True:
            issues_url = data['links']['issues']['href']
            issues = values_from_all_pages(issues_url)
            total_issues += len(issues)

    profile_data['account_size'] = account_size
    profile_data['language_count'] = language_count
    profile_data['total_commits'] = total_commits
    profile_data['total_issues'] = total_issues

    return profile_data
    

# TODO: handle pages for Github!
# This will only give the first "page" of the result set, which is set at 30 items by default. You can use ?per_page=100 to get the maximum ammount but if a user has more than a hundred repos you will need to follow several next URLs in the HTTP Link header send with the response

# TODO: make distinction between original vs. forked for Bitbucket

# TODO: merge both datasets

# TODO: tests + documentation
