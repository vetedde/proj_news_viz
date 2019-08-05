# -*- coding: utf-8 -*-

import os
import sys

from collections import Counter

def print_line_out(article_id, text):
    """
    Converts text to vw format:
    $article_id |text token1:count1 token2:count2 etc...
    """
    line = " ".join("{}:{}".format(key, val) for (key, val) in Counter(text.split()).items())
    return "article_{} |text {}".format(article_id, line)

