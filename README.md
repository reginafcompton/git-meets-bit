# git-meets-bit

This simple flask app presents an API that aggregates profile data from Github and Bitbucket. 

### Get started

[Create a virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/install.html), and install the requirements:

```bash
mkvirtualenv git-meets-bit
pip install -r requirements.txt
```

Create a secrets file, and in it, put your Github access token [(used to authenticate through Github)](https://developer.github.com/v3/#authentication). 

```bash
cp secrets.py.example secrets.py
```

Run the app!

```bash
flask run
```

Looking for someone special? Simply query the tool with an endpoint like so:

```
# the venerable Derek!
http://127.0.0.1:5000/api/v1/users?github=derekeder&bitbucket=derekeder
```

N.b., the API does not expect the user to have the same Bitbucket and Github name, which allows for precision but also some flexibility in shaping your query, e.g., merging two different people.

### Tests

`git-meets-bit` includes the early stages of a test suite, using `pytests`. Run them:

```
pytest
```

### Limitations and places that need improvement

Several aspects of this tool need work:

* The tool does not accommodate "team" users on Bitbucket: you can only merge profiles of individuals. Searching for a team or organization will raise an Internal Server Error. 

* Yuck! An internal server error. That's not terribly graceful. Error catching would be nice.

* The Github API has rate limits, even with an access token: ["For API requests using Basic Authentication or OAuth, you can make up to 5000 requests per hour."](https://developer.github.com/v3/#rate-limiting) In other words, this humble tool could not handle massive user traffic.

Perhaps most importantly, the `git-meets-bit` API loads...very...very...slowly. One immediate fix: do not iterate over the `all_repos` json more than once in `create_github_profile` (e.g., `calculate_repo_counts` and `calculate_total_commits` could benefit from refactoring). I also wonder about writing a multi-threaded solution. (Maybe something that uses concurrency – handling multiple, not necessarily related processes at the same time – or parallelism – breaking one process into multiple smaller tasks?) I do not have much experience with multi-threading, so I did not make an effort to implement such a solution. Until then, enjoy a cup of tea or bag of popcorn, as the json loads...

