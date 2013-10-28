from lxml.html import document_fromstring
from readability import Document
from readability.readability import Unparseable


class ParserException(Exception):
    pass


def parse(item, content_type, text=None, content=None):
    """
    Scrape info from an item

    :param content_type: mime type
    :param text: unicode text
    :param content: byte string
    :param item: Item
    """
    try:
        domain = item.domain
        if text is not None:
            if domain in parse.domains:
                return parse.domains[domain](item, content_type, text)
            else:
                return parse_web_page(text)
    except ParserException:
        pass
    return item.url, ''


parse.domains = {}


def domain_parser(domain):
    """
    Decorator to register a domain specific parser
    :param domain: String
    :return: function
    """
    def decorator(func):
        parse.domains[domain] = func
        return func
    return decorator


def parse_web_page(text):
    """
    Generic wep page parser with readability
    :param text: unicode text
    :return: title, article
    :raise ParserException:
    """
    if not text:
        raise ParserException('No decoded text available, aborting!')
    try:
        doc = Document(text)
    except Unparseable, e:
        raise ParserException(e.message)
    else:
        return doc.short_title(), doc.summary(True)


@domain_parser('github.com')
@domain_parser('bitbucket.org')
def parse_github(item, content_type, text):
    if text is None:
        raise ParserException('Could not decode content')
    doc = document_fromstring(text)
    readme_elements = doc.cssselect('#readme article')
    if readme_elements:
        readme = readme_elements[0]
        readme_title = readme.cssselect('h1')
        if readme_title:
            readme_title[0].drop_tree()
        article = readme.text_content()
    else:
        raise ParserException('readme not found')
    title_elements = doc.cssselect('title')
    if title_elements:
        title = title_elements[0].text_content()
    else:
        raise ParserException('title not found')
    return title, article
