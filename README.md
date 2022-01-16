# export-gh-issues
Scripts to export GitHub issues to json or csv. One day will script over beta projects (when the API is ready)

# export-labelled-gh-issues.py

Usage:
```
python -m export-labelled-gh-issues.py -h
```

Use this script to collect issues (that aren't PRs) from one or more openedx GitHub repos. By default, filtering filters all issues on the label `decoupling`.

positional arguments:
  action      can be one of `export_raw` (export all repo issues to json),`export_filtered` (export filtered issues to json), and `csv_filtered` (export filtered issues to csv)
  repos       One or more openedx repos to grab issues from

optional arguments:
  -h, --help  show this help message and exit



Remaining TODOs:

* The script could be made more flexible by forcing users to specify ORG/REPO. However I'm lazy and my use case is only in one org.

* The script should be made more flexible with respect to label filtering. Adding a `label=` command line option
would be ideal.
