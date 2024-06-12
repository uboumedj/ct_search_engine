from collections import *
import math
import re
import os
import pickle
from nltk.corpus import stopwords


# Necessary to be able to pickle the index
def create_defaultdict():
    return defaultdict(int)


class SearchEngine:
    def __init__(self, dataset, index_path):
        self.database = dataset
        print(dataset)
        self.index = defaultdict(create_defaultdict)
        self.saturation_parameter = 1.2
        self.length_parameter = 0.75
        self.index_path = index_path
        self._index_content()

    def search(self, query):
        """
        Searches the user's query among the database's articles, adding up the bm25 score
        for each keyword from the query.
        Parameters:
            query (str): the user's entire query
        Returns:
            A dict containing the score per article of the user's query, ordered in a descending manner
        """
        normalized_query = query.lower()
        normalized_query = query.strip(".,;:()°")
        query_keywords = normalized_query.split(" ")
        query_keywords = self._reduce_query(query_keywords)
        article_scores = {}
        for word in query_keywords:
            word_score_per_article = self._compute_bm25_score(word)
            article_scores = self._update_scores(article_scores, word_score_per_article)
        article_scores = dict(sorted(article_scores.items(), key=(lambda x : x[1]), reverse=True))
        return article_scores
    
    def _reduce_query(self, query_keywords):
        """
        Attempts to reduce the query response time, by removing keywords that are too
        common, only if the query contains keywords that are less common.
        Parameters:
            query_keywords (list): the list of words from the user's query
        Returns:
            The (eventually) reduced list of words
        """
        unusual_word_count = 0
        freq = []
        for i, word in enumerate(query_keywords):
            freq.append(len(self.index[word]))
            if freq[i] < len(self.database) / 4:
                unusual_word_count += 1
        if unusual_word_count > 0:
            reduced_keywords = []
            for i, word in enumerate(query_keywords):
                if freq[i] < len(self.database) / 4:
                    reduced_keywords.append(query_keywords[i])
            return reduced_keywords
        return query_keywords

    def _compute_bm25_score(self, word):
        """
        Calculates the BM25 score of a single word per article containing it
        Parameters:
            word (str): the word we want to evaluate
        Returns:
            A dict containing the scores of this word per article
        """
        result = {}
        idf = self._inverse_document_frequency(word)
        avgdl = self._average_article_length()
        for article, frequency in self._get_articles_from_word(word).items():
            article_length = len(self.database[self.database['article_id'].str.contains(article)]['texte'].iloc[0])
            tf = frequency * (self.saturation_parameter + 1)
            tf /= frequency + self.saturation_parameter * (1 - self.length_parameter + self.length_parameter * article_length / avgdl)
            tfidf = idf * tf
            result[article] = tfidf
        return result
    
    def _index_content(self):
        """
        Indexes the database's content into a dict containing, for each
        singular word, the occurence per article.
        """
        if os.path.isfile(self.index_path):
            print(f"Loading pre-existing index from {self.index_path}...")
            index_file = open(self.index_path, "rb")
            self.index = pickle.load(index_file)
            print("Loading complete !")
        else:
            print("Indexing articles from code_du_travail.csv...")
            for i, row in self.database.iterrows():
                word_list = self._get_words_from_row(row)
                for word in word_list:
                    self.index[word][row['article_id']] += 1
            index_file = open(self.index_path, "wb")
            pickle.dump(self.index, index_file)
            print("Indexing done !")
            print(f"Indexed data saved to {self.index_path}")

    def _update_scores(self, article_scores, word_score_per_article):
        """
        Updates a query score dict by taking into account the scores of a new word
        Parameters:
            article_scores (dict): the 'old' query's score dict
            word_score_per_article (dict): the scores of a new word not taken into account yet
        Returns:
            The updated article scores
        """
        for article, score in word_score_per_article.items():
            if article in article_scores:
                article_scores[article] += score
            else:
                article_scores[article] = score
        return article_scores

    def _get_articles_from_word(self, word):
        """
        Fetches every article containing a given word from the indexed content
        Parameters:
            word (str): the word we're looking for
        Returns:
            The dict associated with the word, containing the wordcount per article
        """
        normalized_word = word.lower()
        normalized_word = normalized_word.strip(".,;:()°")
        return self.index[normalized_word]

    def _get_words_from_row(self, row):
        """
        Extracts every single word from a normalized article, excluding
        words found in nltk's french stopwords list, which are mainly useless
        Parameters:
            row (pd.dataFrame): the article we want the words from
        Returns:
            A list containing every word from the text
        """
        normalized_text = row['texte'].lower()
        normalized_text = normalized_text.replace("l. ", "l")
        normalized_text = normalized_text.replace("r. ", "r")
        normalized_text = normalized_text.replace("d. ", "d")
        normalized_text = normalized_text.replace("l'", "l ")
        normalized_text = re.sub('<.*?>', '', normalized_text)
        
        words = normalized_text.split(" ")
        stop_words = set(stopwords.words('french'))
        for i in range(len(words)):
            words[i] = words[i].strip(".,;:()°")
        clean_words = []
        for word in words:
            if word not in stop_words:
                clean_words.append(word)
        return [word for word in clean_words if word != '']
    
    def _average_article_length(self):
        """
        Calculates the average article length across the entire database
        """
        result = sum(len(article['texte']) for i, article in self.database.iterrows())
        result /= self._number_of_articles()
        return result
    
    def _number_of_articles(self):
        """
        Calculates the number of articles currently registered in the database
        """
        result = len(self.database)
        return result

    def _inverse_document_frequency(self, word):
        """
        Calculates the inverse document frequency (IDF) of a word across the entire database
        Parameters:
            word (str): the word
        Returns:
            The computed IDF value
        """
        number_of_articles = self._number_of_articles()
        document_frequency = len(self._get_articles_from_word(word))
        result = number_of_articles - document_frequency + 0.5
        result /= document_frequency + 0.5
        result = math.log(1 + result)
        return result