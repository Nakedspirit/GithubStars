import os
import typing

import pandas as pd
from datetime import datetime
import requests


class UsernameRepositoryError(ValueError):

    def __init__(self) -> None:
        super().__init__("Argument should be of form username/repository.")


class TooManyRequestsHttpError(Exception):

    def __init__(self) -> None:
        super().__init__("Too many requests.")


class UrlNotFoundError(Exception):

    def __init__(self, repository: str) -> None:
        super().__init__(
            f"Resource not Found. Check that the repository {repository or ''} is correct.")


class HTTPError(Exception):

    def __init__(self, status_code: int) -> None:
        super().__init__("{} HTTP.".format(status_code))


class MissingHyperlinkTagError(Exception):

    def __init__(self) -> None:
        super().__init__("Missing hyperlink tag.")


class MissingHrefAttributeError(Exception):

    def __init__(self) -> None:
        super().__init__("Missing 'href' attribute from hyperlink tag.")


class HrefContentError(Exception):

    def __init__(self, href_content: str) -> None:
        super().__init__(
            f"Wrong 'href' content: '{href_content}'. It should be of form /username.")


class GitHub:
    """
    Creates a GitHub instance for listing the stargazers of a given repository.
    """
    __GITHUB_URL: str = "https://api.github.com/repos"
    __PAGE_SUFFIX: str = "?page="
    __QUERY_LIMIT = 30  # GitHub API search results limit

    __OK_STATUS_CODE: int = 200
    __TOO_MANY_REQUESTS_STATUS_CODE: int = 429
    __NOT_FOUND_STATUS_CODE: int = 404

    def __init__(self, token: str, username: str, repository: str) -> None:
        self.__username: str = username
        self.__repository: str = repository
        self.__token: str = token
        self.repository_url: str = self.get_repository_url()
        self.stargazers_base_url: str = self.get_stargazers_base_url()

    def get_repository_url(self) -> str:
        return os.path.join(self.__GITHUB_URL, self.__username, self.__repository)

    def get_stargazers_base_url(self) -> str:
        return self.get_response(self.repository_url)["stargazers_url"]

    def get_response(self, url: str):
        token = self.__token
        headers = {'Authorization': f'token {token}',
                   'Accept': 'application/vnd.github.v3.star+json'}
        response = requests.get(
            url, headers=headers)

        status_code: int = response.status_code
        if status_code == self.__OK_STATUS_CODE:
            return response.json()
        if status_code == self.__TOO_MANY_REQUESTS_STATUS_CODE:
            raise TooManyRequestsHttpError()
        if status_code == self.__NOT_FOUND_STATUS_CODE:
            raise UrlNotFoundError(os.path.join(
                self.__username, self.__repository))
        raise HTTPError(status_code)

    def get_url_page_template(self, page_number: int) -> str:
        return self.stargazers_base_url + self.__PAGE_SUFFIX + str(page_number)

    def get_stars_amount(self) -> int:
        return self.get_response(self.repository_url)["stargazers_count"]

    def get_all_stargazers(self) -> typing.List[str]:
        page_number: int = 1
        df_list = []
        stars_amount = self.get_stars_amount()
        pages_amount = int(stars_amount / self.__QUERY_LIMIT) + \
            (stars_amount % self.__QUERY_LIMIT > 0)

        while True:
            current_url = self.get_url_page_template(page_number)
            current_data = self.get_response(
                current_url)
            d_tmp = pd.DataFrame.from_dict(current_data)
            df_list.append(d_tmp)

            if page_number > pages_amount:
                break

            page_number += 1

        df = pd.concat(df_list)
        # normalize the column of dictionaries and join it to df
        df = df.join(pd.json_normalize(df.user))
        # drop "user"
        df.drop(columns=['user'], inplace=True)

        return df
