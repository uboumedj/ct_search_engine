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