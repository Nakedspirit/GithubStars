import typing
import argparse
import pandas as pd

from github import GitHub
from github import UsernameRepositoryError, TooManyRequestsHttpError, UrlNotFoundError
from github import MissingHyperlinkTagError, MissingHrefAttributeError, HrefContentError


class GitHubStars(object):

    def __init__(self, token, username: str, repository: str) -> None:
        self.__token: str = token
        self.__username: str = username
        self.__repository: str = repository

    def __get_github(self) -> typing.Optional[GitHub]:
        try:
            github = GitHub(self.__token, self.__username, self.__repository)
        except (UsernameRepositoryError, UrlNotFoundError) as exception_message:
            print(exception_message)
            return None
        return github

    def process(self) -> None:
        github: typing.Optional[GitHub] = self.__get_github()
        if not github:
            return None
        try:
            stargazers_data = github.get_all_stargazers()
            return stargazers_data
        except (TooManyRequestsHttpError, UrlNotFoundError,
                MissingHyperlinkTagError, MissingHrefAttributeError, HrefContentError) as exception_message:
            print(exception_message)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--token", help="Github API token",
                        required=True)
    parser.add_argument("-u", "--username",
                        help="repository owner's username", required=True)
    parser.add_argument("-r", "--repository",
                        help="repository", required=True)
    parser.add_argument("-o", "--output", help="path to the output csv file",
                        required=True)

    return parser.parse_args()


def main():
    args = parse_args()
    stars = GitHubStars(args.token, username=args.username,
                        repository=args.repository)
    data = stars.process()
    if args.output.endswith(".csv"):
        with open(args.output, "w") as fout:
            if isinstance(data, pd.DataFrame):
                data.to_csv(fout, index=None, header=True)
    # elif args.output.endswith(".sql"):
    #     with open(args.output, "w") as fout:
    #         if isinstance(data, pd.DataFrame):
    #             data.to_sql('starred_at', 'user',
    #                         if_exists='replace', index=False)
    else:
        raise ValueError("Only csv output formats are supported. "
                         "So happy you know it after spending hours fetching "
                         "the stuff!")
    print("The result was written to %s" % args.output)


if __name__ == "__main__":
    main()
