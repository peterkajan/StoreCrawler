# Architecture

Architecture decisions are documented in this file.

Since crawling is mostly IO bound and not CPU bound process, the decision is to use AsyncIO because of its following features:
- task switching is cheap compared to multithreading approach
- crawling performance can be further improved by running multiple processes

High level picture of the script is displayed in the sequence diagram bellow:

![Sequence diagram](./sequence_diagram.png)

## Performance
Performance has been analyzed using Pycharm's Profile mode. Result of such analysis on `example_data/stores.csv` dataset is displayed bellow:

![Sequence diagram](./perforamnce.png)

Tasks scheduling and extracting of the data using regex are the most time-consuming tasks and could be investigated for further performance improvements.

## Scaling
Horizontal scaling could be used for further performance improvement. Architecture could be changed as follows:
- domains that should be analyzed are fetched from MQ
- multiple worker processes hosted on multiple machines fetch domains from MQ and perform the scraping and data extractions
- results are stored to database

This scalable architecture is illustrated bellow:

![Scalable architecture](./scalable_architecture.png)
