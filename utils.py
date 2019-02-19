import requests
from collections import defaultdict

from config import HEADERS_GITHUB, GITHUB_ACCESS_TOKEN_URL

def traverse_github_pages(url):
    '''
    Github limits the number of items returned by an endpoint. 

    This function traverses pages by looking for the keyword 'next'
    in the response data. 

    References:
    https://developer.github.com/v3/guides/traversing-with-pagination
    https://stackoverflow.com/questions/33878019/how-to-get-data-from-all-pages-in-github-api-with-python
    '''
    all_data = []
    more_pages = True
    while more_pages: 
        response = requests.get(url, headers=HEADERS_GITHUB)
        all_data.extend(response.json())
        if 'next' in response.links.keys():
            url = response.links['next']['url']
        else: 
            more_pages = False

    return all_data

def calculate_repo_counts(all_repos):
    '''
    Utility function for `create_github_profile`. 

    Iterates over a list of dicts with all repos 
    belonging to a user to determine the total 
    number of repos forked and original repos.

    Warning! Not very efficient. The calculations in this function 
    should be bundled together with others that require 
    iterating over the repo data.
    '''
    total_forked_repos = len([data for data in all_repos if data['fork'] == True])
    total_original_repos = len([data for data in all_repos if data['fork'] == False])

    repo_counts = {'total_forked_repos': total_forked_repos, 
    'total_original_repos': total_original_repos}
    
    return repo_counts

def calculate_total_commits(all_repos):
    total_commits = 0
    for data in all_repos:
        if data['fork'] == False:
            commits = requests.get(data['commits_url'] + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB) 
            total_commits += len(commits.json())

    return total_commits

def calculate_language_count(all_repos):
    language_count = defaultdict(int)

    for data in all_repos:
        languages_data = requests.get(data['languages_url'] + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB)
        languages = languages_data.json().keys()

        for lang in languages:
            language_count[lang] += 1

    return language_count

def calculate_topic_count(all_repos):
    topic_count = defaultdict(int)

    for data in all_repos:
        topics_data = requests.get(data['url'] + '/topics' + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB)
        topics = topics_data.json()['names']

        for topic in topics:
            topic_count[topic] += 1

    return topic_count

def traverse_bitbucket_pages(url):
    all_values = []
    more_pages = True
    while more_pages: 
        data = requests.get(url).json()
        all_values.extend(data['values'])
        if data.get('next'):
            url = data['next']
        else:
            more_pages = False

    return all_values

def aggregate_profile_data(git_data, bit_data):
    aggregate_data = {}

    summables = ['follower_count', 
                 'open_issues_count', 
                 'account_size',
                 'total_commits']
    
    for key in summables:
        aggregate_data[key] = git_data[key] + bit_data[key]

    total_public_repos = git_data['total_public_repos']
    for repo_type, count in bit_data['total_public_repos'].items():
        total_public_repos[repo_type] += count
    aggregate_data['total_public_repos'] = total_public_repos

    language_count = git_data['language_count']
    for lang, count in bit_data['language_count'].items():
        language_count[lang] += count
    aggregate_data['language_count'] = language_count

    aggregate_data['stars_given_count'] = git_data['stars_given_count']
    aggregate_data['stargazers_count'] = git_data['stargazers_count']
    aggregate_data['topic_count'] = git_data['topic_count']

    return aggregate_data