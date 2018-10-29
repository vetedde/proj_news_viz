import re


def is_valid_topic(raw_topic: str) -> str:
    """
    Validates topic by several rules
    :param raw_topic: raw topic string
    :return: a validated topic or '' if the topic is invalid
    """
    whitespaces = len(re.findall(r"(\s|-|_)", raw_topic))
    low_case = len(re.findall(r"[a-z]", raw_topic))
    upper_case = len(re.findall(r"[A-Z]", raw_topic))
    numbers = len(re.findall(r"\d", raw_topic))
    if upper_case > whitespaces and low_case != 0:
        return ''
    elif low_case == 0 and upper_case == 0:
        return ''
    elif re.search(r"^\d", raw_topic) and numbers > 4:
        return ''
    elif upper_case and numbers and not whitespaces:
        return ''
    elif re.search(r"(\.html|\.php|\.xml|\.csv)", raw_topic):
        return ''
    elif len(raw_topic) <= 1:
        return ''
    else:
        return raw_topic.lower()


def process_topic(url: str) -> str:
    """
    Runs topic processing from a source URL
    :param url: source URL
    :return: topic text
    """
    topic = re.sub(r"(https://|http://)", '', url).split("/")[1]
    if re.search('[a-zA-Z]', topic) and not re.search(r'(\?|=)', topic):
        return is_valid_topic(topic)
    else:
        return ''
