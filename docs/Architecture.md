# Architecture

Since crawling is mostly IO bound and not CPU bound process, AsyncIO approach is most suitable because of its following features:
- task switching is cheap compared to multithreading approach
- crawling performance can be still further improved by running multiple processes

High level picture of the script is displayed in the sequence diagram bellow:

![Sequence diagram](./sequence_diagram.png)

## Performance
Performance has been analyzed using Pycharm's Profile mode. Result of such analysis on `example_data/stores.csv` dataset is displayed bellow:

![Sequence diagram](./perforamnce.png)

Tasks scheduling and data extraction using regex are the most time-consuming tasks and could be investigated for further performance improvements.

## Scaling
Horizontal scaling could be used for scaling the crawler for more domains. Architecture could be changed as follows:
- domains are fetched from MQ
- multiple worker processes hosted on multiple machines fetch domains from MQ and perform the scraping and data extractions
- workers store results to the database

This scalable architecture is illustrated bellow:

![Scalable architecture](./scalable_architecture.png)
