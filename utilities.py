import pandas as pd
import time


def read_csv(file_path):
    """
    Reads the csv file located at specified path and returns its content
    Parameters:
        file_path (str): the csv file's location
    Returns:
        The contents inside a Pandas Dataframe
    """
    if (not isinstance(file_path, str)):
        print("error: Path of dataset file must be a string")
        return None
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        print("error: Specified file was not found")
        return None
    return data


def extract_titles(title_string):
    """
    Transforms the path_title data into a readable list of titles
    Parameters:
        title_string (str): the string containeed in the path_title column
    Returns:
        A list of titles extracted from the string
    """
    title_string = title_string.strip("[]")
    titles = title_string.split(",")
    for i in range(len(titles)):
        titles[i] = titles[i].strip(' "')
    return titles


def convert_date(timestamp):
    """
    Converts a date from the str timestamp found in the dataset
    into a real date.
    Parameters:
        timestamp (str): a timestamp in str format and in milliseconds
    Returns:
        The correctly formatted date
    """
    try:
        timestamp = float(timestamp) / 1000.0
    except:
        print("warning: error while converting timestamp to a number")
        return None
    time_info = time.gmtime(timestamp)
    date = time.strftime("%d %b %Y", time_info)
    return date
