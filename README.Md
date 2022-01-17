# Annotation tool for short text classification with Human in the Loop -- Name TBD
An annotation tool for classifying short text such as tweets or phrases which
were pre processed.
The idea is that datasets are often too large to be annotated in its entirety by
a human annotator. In order to make this task easier, we are working on an
annotation tool that let's the user create their own labels and annotate a
portion of their datasets. Using a few shot learning algorithm, the rest of the
dataset shall be annotated automatically.
Furthermore, the tool makes suggestions to the annotator by providing
semantically similar results from the dataset in order to find relevant data
points faster.
The annotation tool provides basic project management functionalities for
annotating the same data multiple times, as well as saving the results in a
`.csv` file.
To get an overview of the work in this repo, check out the
[issues][issues], as well as the closed
[pull requests][PRs] where summaries of new features are described.

## How to run?

The code is currently developed on Python 3.9.9, so install that if possible.
Create a virtual environment with
[Pipenv](https://pipenv-fork.readthedocs.io/en/latest/basics.html)
`pipenv install` should install everything you'll need.

In order to run the long callbacks you need to have a redis server and a celery
worker running:

`docker run -p 6379:6379 redis` sets up a docker container for the redis server.

`celery -A app.celery_app worker --loglevel=INFO` sets up the celery worker.
**NOTE:** You have to run this command from the `src` folder!

This will become more convenient at some point, but for now, it has to be started manually.



## Packages used in the application
- [sentence bert](https://www.sbert.net/index.html) for sentence embeddings
- [dash](https://dash.plotly.com/) for the web interface for the user
- [dash bootstrap components][dbc] for the layout and lots of styling of the web
  app
- [faiss](https://faiss.ai/) for fast similarity search

## Questions/Requests?

Feel free to open an issue, I will answer in due time.

[issues]: https://github.com/Leibniz-HBI/anno-itl/issues
[PRs]: https://github.com/Leibniz-HBI/anno-itl/pulls?q=is%3Apr+is%3Aclosed
[dbc]: https://dash-bootstrap-components.opensource.faculty.ai/



