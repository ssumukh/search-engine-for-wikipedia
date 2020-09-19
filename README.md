# WikiPedia Search Engine

Uses Block-Sort-Based-Indexing to create the inverted index of the entire WikiPedia dump (73.3 GB), then queries on the index and retrieves top 10 results via relevance ranking of the documents, implemented using tf-idf scoring.

## Data

The WikiPedia dump can be found here on this [link](https://drive.google.com/file/d/1QMpM1CSn6j8Hwu5AabTqTQ1km9xCzSEV/view?usp=sharing). It is a zip file, and it should be around 73.3 GB in disk size when extracted.

## Setting up the environment

This environment is for python 3.7.3

To install it on your systems:

1. Install conda
2. Run "conda env create -f environment.yml" 
3. Run "conda activate search_eng"

## Steps to run

Make sure that the enviroment is setup, and the data is downloaded and you have extracted the zip file.

1. Creating the inverted index - ```bash index.sh <path-to-wiki-dump> <path-to-invertedindex (outputfile)>```
	Please note that this step will take time.
2. Querying with the index - ```bash search.sh <path-to-invertedindex> <query>```
	Example query could be *India*

## Field Query Details

Support for Field Queries . Fields include Title, Infobox, Body, Category, Links, and References of a Wikipedia page. This helps when a user is interested in searching for the movie ‘Up’ where he would like to see the page containing the word ‘Up’ in the title and the word ‘Pixar’ in the Infobox.

## References

* http://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf [Chapters 1-5]
* Information Retrieval: Algorithms and Heuristics. D.A. Grossman, O. Frieder. Springer, 2004. 