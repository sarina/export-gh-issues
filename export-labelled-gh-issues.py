#!/usr/bin/env python3
"""
Usage:
    python -m export-labelled-gh-issues.py -h
"""

# pylint: disable=unspecified-encoding
import json
import logging
import os
import sys
import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime

import github as gh_api
import requests

from pandas import json_normalize

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
LOG = logging.getLogger(__name__)


def main(action, repos):
    """
    Script entrypoint
    """
    gh_headers = get_github_headers()

    stamp = datetime.utcnow().isoformat()[0:19]
    export_filename = f"output/{action}-{stamp}.json".format(action=action, stamp=stamp)

    if action == "export_raw":
        with open(export_filename, "w") as export_file:
            export_file.write("# Export from: {stamp}\n# Repos: {repos}".format(
                stamp=stamp, repos=repos
            ))


        get_and_filter_issues(repos, gh_headers, export_filename, export_type="raw", label="decoupling")

    elif action == "export_filtered":
        with open(export_filename, "w") as export_file:
            export_file.write("# Export from: {stamp}\n# Repos: {repos}".format(
                stamp=stamp, repos=repos
            ))


        get_and_filter_issues(repos, gh_headers, export_filename, export_type="filtered", label="decoupling")

    elif action == "csv_filtered":
        export_filename = f"output/{action}-{stamp}.csv".format(action=action, stamp=stamp)
        get_and_filter_issues(repos, gh_headers, export_filename, export_type="filtered", label="decoupling", csv=True)

    else:
        print("Not sure how we got here, try again")
        
def get_and_filter_issues(all_repos, gh_headers, export_filename, export_type="filtered", label=None, csv=False):
    """
    Get all issues that are not PRs from the specified repo.
    * export_filename: the name of the file you'd like your data exported to
    * export_type: Either filtered (applies hardcoded filters, for now), or raw
    * label: only return issues with the given label.
    * csv: if True, returns a flattened CSV instead of a json; without filtering, this may not work.
    """
    all_issues = []
    for repo in all_repos:
        print("grabbing repo {0}".format(repo))
        url = "https://api.github.com/repos/openedx/{repo}/issues".format(repo=repo)
        for issue in requests.get(url, headers=gh_headers).json():
            all_issues.append(issue)
    saved_issues = []

    # Variables needed for doing hard-coded filtering of the issue to only the specified fields
    # Keys with single values: "key" : "value"
    keys_to_save = ["url", "number", "title", "body", "created_at", "updated_at"]
    # Keys that have keys nested in a dict: "key": { {nkey: value}, {nkey2: value} }
    nested_keyvalues = [{"user": "login"}]

    # Keys that follow with a list of dicts: "key": [{nkey: value}, {nkey2: value}]
    listed_keyvalues = [{"labels": "name"}, {"assignees": "login"}]

    for issue in all_issues:
        # all prs are issues, but not all issues are prs. grab just the issues        
        if 'pull_request' in issue:
            continue

        # Filter out issues that don't have the given label, but return all issues in the Decoupling project
        if label and "decoupling" not in issue["url"]:
            # filter on those with only the label, but skip decoupling project
            match = [1 for item in issue["labels"] if item['name']==label] != []
            if not match:
                continue

        if export_type == "filtered":
            # Extract the fields we need
            new_issue = {}
            for k in keys_to_save:
                v = issue[k]
                new_issue[k] = v

            for keypair in nested_keyvalues:
                k1 = [*keypair][0]
                k2 = keypair[k1]
                v = issue[k1][k2]
                # Flattening the tree for CSV conversion
                if csv:
                    new_issue["{k1}-{k2}".format(k1=k1, k2=k2)] = v
                else:
                    new_issue[k1] = {}
                    new_issue[k1][k2] = v

            for keypair in listed_keyvalues:
                k1 = [*keypair][0]
                k2 = keypair[k1]
                
                for k1dict in issue[k1]:
                    v = k1dict[k2]
                    if csv:
                        # flattening for csv conversion
                        dkey = "{k1}-{k2}".format(k1=k1, k2=k2)
                        if dkey not in new_issue:
                            new_issue[dkey] = []
                        new_issue[dkey].append(v)
                    else:
                        if k1 not in new_issue:
                            new_issue[k1] = []
                        new_issue[k1].append({k2: v})
                        
            # once new_issue is built out at end of "filtered" section, rename it for following line
            issue = new_issue
        # Append the edited issue to the list of issues we're saving
        saved_issues.append(issue)
    if csv:
        issue_dataframe = json_normalize(saved_issues)
        issue_dataframe.to_csv(export_filename, index=False)

    else:
        with open(export_filename, "a") as export_file:
            print(json.dumps(saved_issues, indent=4), file=export_file)

    print("Successfully wrote issues to: {0}".format(export_filename))

def get_github_headers() -> dict:
    """
    Load GH personal access token from file.
    """
    gh_token = os.environ["GITHUB_TOKEN"]
    LOG.info(" Authenticating.")
    gh_client = gh_api.Github(gh_token)
    LOG.info(" Authenticated.")

    # set up HTTP headers because PyGithub isn't able to determine team permissions                                                                     # on a repo in bulk.                                                                                                                             
    gh_headers = {"AUTHORIZATION": f"token {gh_token}"}
    return gh_headers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Use this script to collect issues (that aren't PRs) from one or more openedx GitHub repos.\nBy default, filtering filters all issues on the label `decoupling`.")

    parser.add_argument('action',
                        help="can be one of `export_raw` (export all repo issues to json),`export_filtered` (export filtered issues to json), and `csv_filtered` (export filtered issues to csv)",
                        default='export_filtered')

    parser.add_argument('repos',
                        help="One or more openedx repos to grab issues from",
                        nargs='+')

    args = parser.parse_args()
    main(args.action, args.repos)

