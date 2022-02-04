from urllib.parse import urlparse


def get_root_url(request_url):
    """ Get root URL of this deployed system, which consists of schema, hostname, and port

    :param request_url:
    :return:
    """
    parsed_url = urlparse(request_url)
    return "{}://{}:{}".format(
        parsed_url.scheme, parsed_url.hostname, parsed_url.port
    )
