import requests
from collections import defaultdict

from flask import request
from flask import jsonify, redirect, url_for
from flask import Flask

from config import HEADERS_GITHUB, BASE_URL_GITHUB, GITHUB_ACCESS_TOKEN_URL
from utils import traverse_github_pages, calculate_repo_counts, calculate_total_commits, calculate_language_count, calculate_topic_count, traverse_bitbucket_pages, aggregate_profile_data

app = Flask(__name__)

# users?bitbucket=reginacomp&github=reginafcompton
@app.route('/api/v1/users', methods=['GET'])
def users_view():
    git_username = request.args.get('github')
    bit_username = request.args.get('bitbucket')

    git_data = create_github_profile(git_username)
    bit_data = create_bitbucket_profile(bit_username)
    aggregate_data = aggregate_profile_data(git_data, bit_data)

    return jsonify(aggregate_data)


def create_github_profile(git_username):
    base_url_github = BASE_URL_GITHUB + git_username
    profile_data = {}
    
    url = base_url_github + '/repos' + GITHUB_ACCESS_TOKEN_URL + '&per_page=100'

    all_repos = traverse_github_pages(url)

    profile_data['total_public_repos'] = calculate_repo_counts(all_repos)

    followers_url = base_url_github + '/followers' + GITHUB_ACCESS_TOKEN_URL + '&per_page=100'
    profile_data['follower_count'] = len(traverse_github_pages(followers_url))

    starred_url = base_url_github + '/starred' + GITHUB_ACCESS_TOKEN_URL + '&per_page=100'
    profile_data['stars_given_count'] = len(traverse_github_pages(starred_url))

    stargazers_count = 0
    open_issues_count = 0
    account_size = 0
    for data in all_repos:
        stargazers_count += data['stargazers_count']
        open_issues_count += data['open_issues_count']
        account_size += data['size']

    profile_data['stargazers_count'] = stargazers_count
    profile_data['open_issues_count'] = open_issues_count
    profile_data['account_size'] = account_size
    profile_data['total_commits'] = calculate_total_commits(all_repos)
    profile_data['language_count'] = calculate_language_count(all_repos)
    profile_data['topic_count'] = calculate_topic_count(all_repos)

    return profile_data


def create_bitbucket_profile(bit_username):
    # Concept of stars and topics does not apply to Bitbucket
    base_url_bitbucket = "https://api.bitbucket.org/2.0/{endpoint}/{username}"
    profile_data = {}
    
    # Get all repo data
    repos_url = base_url_bitbucket.format(endpoint='repositories', username=bit_username)
    repositories = traverse_bitbucket_pages(repos_url)

    # Followers
    followers_url = base_url_bitbucket.format(endpoint='users', username=bit_username) + '/followers'
    followers = traverse_bitbucket_pages(followers_url)
    profile_data['follower_count'] = len(followers)

    total_forked_repos = 0
    total_original_repos = 0
    account_size = 0
    language_count = defaultdict(int)
    total_commits = 0 
    open_issues_count = 0
    for data in repositories:
        if data.get('parent'):
            total_forked_repos += 1
        else:
            total_original_repos += 1

        account_size += data['size']
        
        if data['language']:
            language_count[data['language']] += 1

        if not data.get('parent'):
            commits_url = data['links']['commits']['href']
            commits = traverse_bitbucket_pages(commits_url)
            total_commits += len(commits)

        if data['has_issues'] == True:
            issues_url = data['links']['issues']['href']
            issues = traverse_bitbucket_pages(issues_url)
            open_issues_count += len(issues)

    profile_data['total_public_repos'] = {'total_forked_repos': total_forked_repos, 
                                          'total_original_repos': total_original_repos}
    profile_data['account_size'] = account_size
    profile_data['language_count'] = language_count
    profile_data['total_commits'] = total_commits
    profile_data['open_issues_count'] = open_issues_count


    return profile_data
