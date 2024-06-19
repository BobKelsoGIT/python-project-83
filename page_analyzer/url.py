import validators
from urllib.parse import urlparse


def validate_url(url):
    return validators.url(url)


def normalise_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
