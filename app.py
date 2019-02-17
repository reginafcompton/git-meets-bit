import requests

from flask import request
from flask import jsonify, redirect, url_for
from flask import Flask

from config import HEADERS_GITHUB, BASE_URL_GITHUB, GITHUB_ACCESS_TOKEN_URL
from utils import calculate_repo_counts, calculate_total_commits, calculate_language_count, calculate_topic_count

app = Flask(__name__)

# users/githubusername-bitbucketusername
@app.route('/api/v1/users/<usernames>', methods=['GET'])
def user_detail_view(username):
    git_username, bit_username = usernames.replace('-', ' ').split(' ')

    data = create_profile_data(git_username=git_username,
                               bit_username=bit_username)

    return jsonify(r.json())

# users?bitbucket=reginacomp&github=reginafcompton
@app.route('/api/v1/users', methods=['GET'])
def users_view():
    git_username = request.args.get('github', '')
    bit_username = request.args.get('bitbucket', '')

    data = create_profile_data(git_username=git_username,
                               bit_username=bit_username)

    return jsonify(data)


def create_profile_data(git_username=None, bit_username=None):
    base_url_github = BASE_URL_GITHUB + git_username
    profile_data = {}
    
    # Get all repo data
    url = base_url_github + '/repos' + GITHUB_ACCESS_TOKEN_URL
    repos_as_json = requests.get(url, headers=HEADERS_GITHUB).json()

    # Github total number of public repos
    profile_data['total_public_repos'] = calculate_repo_counts(repos_as_json)

    # Github followers
    url = base_url_github + '/followers' + GITHUB_ACCESS_TOKEN_URL 
    resp = requests.get(url, headers=HEADERS_GITHUB)
    profile_data['follower_count'] = len(resp.json())

    # Github stars received
    url = base_url_github + '/starred' + GITHUB_ACCESS_TOKEN_URL
    resp = requests.get(url, headers=HEADERS_GITHUB)
    profile_data['stars_given_count'] = len(resp.json())

    # Github stars received 
    stargazers_count = sum([data['stargazers_count'] for data in repos_as_json])
    profile_data['stargazers_count'] = stargazers_count

    # Github open issues
    open_issues_count = sum([data['open_issues_count'] for data in repos_as_json])
    profile_data['open_issues_count'] = open_issues_count

    # Github total commits
    profile_data['total_commits'] = calculate_total_commits(repos_as_json)

    # Account size
    account_size = sum([data['size'] for data in repos_as_json])
    profile_data['account_size'] = account_size

    # Languages
    profile_data['language_count'] = calculate_language_count(repos_as_json)
    
    # Topics 
    profile_data['topic_count'] = calculate_topic_count(repos_as_json)

    return profile_data



# TODO: handle pages!
# This will only give the first "page" of the result set, which is set at 30 items by default. You can use ?per_page=100 to get the maximum ammount but if a user has more than a hundred repos you will need to follow several next URLs in the HTTP Link header send with the response
