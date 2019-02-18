# git-meets-bit

This simple flask app presents an API that aggregates profile data from Github and Bitbucket. Looking for someone? Simply query the tool with an endpoint like so:

```
/api/v1/users?github=datamade&bitbucket=datamade
```

### Get started

Create a virtual environment, and install the requirements:

```bash
mkvirtualenv git-meets-bit
pip install -r requirements.txt
```



### Limitations and places that need improvement

The tool does not accommodate "team" users on Bitbucket: you can still find profile information for Github organizations, but those data will not be consolidated with a corresponding Bitbucket account. 

What happens if the app cannot find a username in either API? An internal server error. That's not terribly graceful. Error catching would be nice.

The Github API has rate limits, even with an access token: ["For API requests using Basic Authentication or OAuth, you can make up to 5000 requests per hour."](https://developer.github.com/v3/#rate-limiting) In other words, this humble tool could not handle massive user traffic.

Perhaps most importantly, the `git-meets-bit` API loads...very...very...slowly. One immediate fix: do not iterate over the `all_repos` json more than once in `create_github_profile` (e.g., calculate_repo_counts and calculate_total_commits could benefit from refactoring). 



