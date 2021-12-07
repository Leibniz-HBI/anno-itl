# Annotation tool for short text classification with Human in the Loop -- Name TBD
An annotation tool for classifying short text such as tweets or phrases which
were pre processed.
The idea is that datasets are often too large to be annotated in its entirety by
a human annotator. In order to make this task easier, we are working on an
annotation tool that let's the user create their own labels and annotate a
portion of teir datasets. Using a few shot learning algorithm, the rest of the
dataset shall be annotated automatically.
Furthermore, the tool makes suggestions to the annotator by providing
semantically similar results from the dataset in order to find relevant data
points faster.


## using
- [sentence bert](https://www.sbert.net/index.html) for sentence embeddings
- [dash](https://dash.plotly.com/) for the web interface for the user
- [faiss](https://faiss.ai/) for fast similarity search


