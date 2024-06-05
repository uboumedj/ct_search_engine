import pandas as pd
import click
import re
import time
import locale
from searchengine import SearchEngine

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


def match_article_num(query, dataset):
    """
    Checks if the user query matches a valid article number from the
    dataset, and returns the corresponding article if it is found.
    Parameters:
        query (str): the user's query
        dataset (pandas dataFrame): the search engine's dataset
    Returns:
        The whole dataFrame row containing the matching entry, or None.
    """
    valid_article_num = re.match("^[LDR]{1}[0-9\-]+$", query)
    if valid_article_num is not None:
        article = dataset[dataset['article_num'].str.contains(query+"$")]
        if not article.empty:
            return article
    return None


def solve_query(query, dataset, engine):
    """
    Tries to solve the user's query using a combination of tools
    Parameters:
        query (str): the string of characters the user queried
        dataset (dataFrame): the search engine's dataset
        engine (SearchEngine): the search engine object
    Returns:
        The "search engine's" result
    """
    results = []
    article_num_check = match_article_num(query, dataset)
    if article_num_check is not None:
        results.append(article_num_check)
    search_results = engine.search(query)
    for article, score in search_results.items():
        article = dataset[dataset['article_id']==article]
        if not article.empty:
            results.append(article)
        if len(results) > 5:
            break
    return results


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


def display_results(user_query, result_list):
    """
    Displays the search results in a readable format
    Parameters:
        user_query (str): the string of characters the user queried
        result_list (list): the search results, returned from solve_query
    """
    number_of_entries = len(result_list)
    print(f"{number_of_entries} résultat(s) correspondant à la requête '{user_query}'.")
    counter = 1
    for entry in result_list:
        print(f"\n>>>>>>>>>>>>>>>>>>>> Résultat n.{counter} <<<<<<<<<<<<<<<<<<<<<")
        print(f"ID Base de données: {entry['article_id'].iloc[0]}")
        print(f"Article {entry['article_num'].iloc[0]}")
        print(f"En vigueur depuis: {convert_date(entry['date_deb'].iloc[0])}")
        print("\n")
        for title in extract_titles(entry['path_title'].iloc[0]):
            print(title)
        print("\n")
        article_text = entry['texte'].iloc[0].replace("<p>", "").replace("</p>", "\n\n")
        article_text = re.sub('<.*?>', '', article_text)
        print(f"{article_text}")
        counter += 1


def query_loop(dataset, engine):
    """
    Main logic loop of the program
    Parameters:
        dataset (pandas dataFrame): the search engine's dataset
        engine (SearchEngine): the search engine containing the indexed content
    """
    query = input("Query: ")
    results = solve_query(query, dataset, engine)
    display_results(query, results)
    query_loop(dataset, engine)


@click.command()
@click.option('--file', default='./code_du_travail.csv', help='CSV file path')
def main(file):
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    dataset = read_csv(file)
    engine = SearchEngine(dataset=dataset)
    query_loop(dataset, engine)


if __name__ == "__main__":
    main()
