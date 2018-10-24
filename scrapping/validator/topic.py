import re


def valid_topic(raw_topic: str) -> str:
    """
    Validates topic by the several rules
    :param raw_topic: raw topic string
    :return: a validated topic or '' if the validation process didn't pass
    """
    whitespaces = len(re.findall(r"(\s|-|_)", raw_topic)) if re.search(r"(\s|-|_)", raw_topic) else 0
    low_case = len(re.findall(r"[a-z]", raw_topic)) if re.search(r"[a-z]", raw_topic) else 0
    upper_case = len(re.findall(r"[A-Z]", raw_topic)) if re.search(r"[A-Z]", raw_topic) else 0
    numbers = len(re.findall(r"\d", raw_topic)) if re.search(r"\d", raw_topic) else 0
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
        return valid_topic(topic)
    else:
        return ''
