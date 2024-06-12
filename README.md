# A Search Engine to search through the French Labor Code (Code du Travail)

The dataset is located in the .csv file, representing every article of the french labor code.

The search engine uses simple **BM25/TF-IDF** scoring to compute the relevance of each article towards the user's query.

## Python libraries used

* **nltk** (*stopwords, stemming*)
* **pandas** (*data structure*)
* **pickle** (*index saving/retrieval*)
* **fastAPI** (*small app with interface*)

### What should be improved

BM25 search with Python is very slow. With a single term, search delay is reasonable. With multiple terms, it becomes cumbersome. Needs improvement.

Also, might take a look at LLMs for query augmentation.
