# GitHub Stars

This is the Python script to fetch star count information from the repository
on GitHub.

## Setup

[typing](https://docs.python.org/3/library/typing.html) &&
[pandas](https://pandas.pydata.org) must be installed:

```
pip3 install -r requirements.txt
```

Besides, you must get the token to access GitHub API at full limit
(Settings -> Personal access tokens).

## Usage

```
python3 github_stars.py -i [github token] -u [username] -r [repository] -o [your_file].csv
```

Example:

```
python3 github_stars.py -i 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 -u groner -r pythinkgear -o stars.csv
```

List of arguments:

-h, --help show this help message and exit
-i TOKEN, --token TOKEN
Github API token
-u USERNAME, --username USERNAME
repository owner's username
-r REPOSITORY, --repository REPOSITORY
repository
-o OUTPUT, --output OUTPUT
path to the output csv file

## How it works

We query the data using the GitHub API, then create a data frame with the data which is saved in CSV

## License

MIT.
