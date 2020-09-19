IRE mini project phase 2

[Ubuntu 16.04]
[Python 2.7, with all the libraries mentioned in the environment file]

Run the below in the terminal to increase concurrent open files limit
> ulimit -n 10000

Steps:

To run in the indexer

> bash index.sh <path to xml dump> <path to directory where index is supposed to be stored>

To run the queries:

> bash search.sh <path to index directory created above>

Type in the query and press enter to search for it. Top 10 will be displayed along with search time.
Enter 'exit' to exit the loop, or press CTRL+C