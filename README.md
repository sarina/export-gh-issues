# export-gh-issues
Scripts to export GitHub issues to json or csv. One day will script over beta projects (when the API is ready)

# export-labelled-gh-issues.py

Usage:
```
python -m export-labelled-gh-issues.py -h
```

Use this script to collect issues (that aren't PRs) from one or more GitHub repos.
The first script argument can be one of `export_raw`,`export_filtered`, and `csv_filtered`.
Currently, the 'filtered' option is hardcoded to filter on the label 'decoupling'.
"You may then list the name of one or more openedx repos (just the repo name). The openedx org is hardcoded.
Example usage: `python -m export-labelled-gh-issues.py export_filtered tcril-engineering`
Resulting .json or .csv files go to the output/ folder.

Remaining TODOs:

* The script could be made more flexible by forcing users to specify ORG/REPO. However I'm lazy and my use case is only in one org.

* The script should be made more flexible with respect to label filtering. Adding a `label=` command line option
would be ideal.
