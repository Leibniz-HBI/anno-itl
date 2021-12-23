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


## Using
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
