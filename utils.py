import requests
from collections import defaultdict

from config import HEADERS_GITHUB, GITHUB_ACCESS_TOKEN_URL

def calculate_repo_counts(repos_as_json):
    total_forked_repos = len([c for c in repos_as_json if c['fork'] == True])
    total_original_repos = len([c for c in repos_as_json if c['fork'] == False])

    repo_counts = {'total_forked_repos': total_forked_repos, 
    'total_original_repos': total_original_repos}
    
    return repo_counts

def calculate_total_commits(repos_as_json):
    total_commits = 0;
    for data in repos_as_json:
        if data['fork'] == False:
            commits = requests.get(data['commits_url'] + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB) 
            total_commits += len(commits.json())

    return total_commits

def calculate_language_count(repos_as_json):
    language_count = defaultdict(int)

    for data in repos_as_json:
        languages_data = requests.get(data['languages_url'] + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB)
        languages = languages_data.json().keys()

        for lang in languages:
            language_count[lang] += 1

    return language_count

def calculate_topic_count(repos_as_json):
    topic_count = defaultdict(int)

    for data in repos_as_json:
        topics_data = requests.get(data['url'] + '/topics' + GITHUB_ACCESS_TOKEN_URL, headers=HEADERS_GITHUB)
        topics = topics_data.json()['names']

        for topic in topics:
            topic_count[topic] += 1

    return topic_count
