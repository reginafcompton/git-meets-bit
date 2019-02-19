import pytest

from utils import calculate_repo_counts, calculate_total_commits, calculate_language_count, calculate_topic_count

'''
This test suite hardly provides full coverage. It only considers four utility functions.

Some more aspects of the app that require testing:
- test the efficacy of `aggregate_profile_data`: does it sum together two dictionaries?
- test the git-meets-bit API route itself: does it return the expected json when the url contains correct params (bitbucket and github usernames)?
- test the creation of Bit vs. Git profiles: do `create_github_profile` and `create_bitbucket_profile` return dicts with data as expected? 
- overall, these tests need more data mocking (see note below): as they stand, they're not very stable, i.e., if a DataMade coder updates one of the repos in conftest, the tests will likely break.
'''

def test_calculate_repo_counts(all_repos):
    repo_counts = calculate_repo_counts(all_repos)

    assert repo_counts['total_forked_repos'] == 3
    assert repo_counts['total_original_repos'] == 2

# Warning! The following tests are not stable, since 
# the functions themselves put in data via GET requests. 
# Ideally, those requests would be mocked with appropriate test data.  
def test_calculate_total_commits(all_repos):
   assert calculate_total_commits(all_repos) == 4

@pytest.mark.parametrize('language,count', [
    ('Ruby', 4),
    ('HTML', 4),
    ('R', 1), 
    ('Makefile', 2),
    ('CSS', 4), 
    ('JavaScript', 4),
    ('Python', 4),
])
def test_calculate_language_count(all_repos, language, count):
    language_count = calculate_language_count(all_repos)

    assert language_count[language] == count

@pytest.mark.parametrize('topic,count', [
    ('city-zoning', 1),
    ('javascript', 1),
    ('chicago', 1),
])
def test_calculate_topic_count(all_repos, topic, count):
    topic_count = calculate_topic_count(all_repos)
   
    assert topic_count[topic] == count
