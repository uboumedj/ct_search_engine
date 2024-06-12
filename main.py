import click
import re
import os
import locale
from searchengine import SearchEngine
from utilities import extract_titles, read_csv, convert_date


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
    search_results = engine.search(query)
    for article, score in search_results.items():
        article = dataset[dataset['article_id']==article]
        if not article.empty:
            results.append(article)
        if len(results) > 5:
            break
    return results


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
@click.option('--index', default='./index_cdt.pkl', help='Generated index\'s file path')
@click.option('--retrain', default=False, is_flag=True, help='Whether to re-index the content or not')
def main(file, index, retrain):
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    dataset = read_csv(file)
    if retrain == True:
        if os.path.isfile(index) and re.match("^\..*\.pkl", index):
            os.remove(index)
    engine = SearchEngine(dataset=dataset, index_path=index)
    query_loop(dataset, engine)


if __name__ == "__main__":
    main()
