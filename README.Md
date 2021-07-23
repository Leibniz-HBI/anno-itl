# Clustering arguments in python
Project for argument clustering in python.
Furthermore the start of an annotation tool for FAME.

## using
- sentence bert for sentence embeddings
- clustering: TBD
maybe faiss is too much at this point for storing the embeddings, will only be a
few.

data is in `../datasets/gw_cluster`

## Notes:
- Flair is in dev-packages for now, since it has a dependency conflict with
  sentence-transformes due to different torch dependencies.



