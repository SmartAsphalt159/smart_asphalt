"""
    File is meant to offer debug statements that can be turned on or off if needed
"""


def print_verbose(string_text, flag):
    """
    Prints if flag is true otherwise disables printing
    :param string_text: A string of any length
    :param flag: A bool
    :return:
    """
    if flag is True:
        print(string_text)