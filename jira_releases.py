#!/usr/bin/env python3

import argparse
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
from urllib.parse import quote


def get_project_versions(jira_url, project_key, username, api_token):
    """
    Fetches all versions (releases) for a given Jira project.
    
    Args:
        jira_url (str): Base URL of the Jira instance (e.g., 'https://your-domain.atlassian.net')
        project_key (str): The key of the Jira project (e.g., 'PROJ')
        username (str): Jira username or email
        api_token (str): Jira API token
    
    Returns:
        list: List of version objects
    """
    # Ensure the URL doesn't end with a slash
    if jira_url.endswith('/'):
        jira_url = jira_url[:-1]
    
    # Build the API endpoint URL
    api_endpoint = f"{jira_url}/rest/api/2/project/{project_key}/versions"
    
    try:
        response = requests.get(
            api_endpoint,
            auth=HTTPBasicAuth(username, api_token),
            headers={"Accept": "application/json"}
        )
        
        # Raise an exception for 4XX and 5XX status codes
        response.raise_for_status()
        
        # Return the parsed JSON response
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.status_code == 401:
            print("Authentication failed. Please check your username and API token.")
        elif response.status_code == 403:
            print("You don't have permission to access this resource.")
        elif response.status_code == 404:
            print(f"Project '{project_key}' not found.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Connection Error: Failed to connect to the Jira server.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Timeout Error: The request timed out.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_issues_for_version(jira_url, project_key, version_id, username, api_token):
    """
    Fetches all issues associated with a specific version (release).
    
    Args:
        jira_url (str): Base URL of the Jira instance
        project_key (str): The key of the Jira project
        version_id (str): The ID of the version to fetch issues for
        username (str): Jira username or email
        api_token (str): Jira API token
    
    Returns:
        list: List of issue objects
    """
    # Ensure the URL doesn't end with a slash
    if jira_url.endswith('/'):
        jira_url = jira_url[:-1]
    
    # Construct JQL query to find issues with the specified fix version
    jql_query = f"project = {project_key} AND fixVersion = {version_id} ORDER BY key ASC"
    encoded_jql = quote(jql_query)
    
    # Build the API endpoint URL
    api_endpoint = f"{jira_url}/rest/api/2/search?jql={encoded_jql}&maxResults=1000"
    
    try:
        response = requests.get(
            api_endpoint,
            auth=HTTPBasicAuth(username, api_token),
            headers={"Accept": "application/json"}
        )
        
        # Raise an exception for 4XX and 5XX status codes
        response.raise_for_status()
        
        # Return the parsed JSON response
        return response.json().get("issues", [])
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.status_code == 401:
            print("Authentication failed. Please check your username and API token.")
        elif response.status_code == 403:
            print("You don't have permission to access this resource.")
        elif response.status_code == 400:
            print(f"Bad request: Invalid JQL query or parameters.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Connection Error: Failed to connect to the Jira server.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Timeout Error: The request timed out.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)


def display_issues(issues, output_format="text"):
    """
    Displays the issues in the specified format.
    
    Args:
        issues (list): List of issue objects
        output_format (str): Output format ('text', 'json')
    """
    if output_format == "json":
        print(json.dumps(issues, indent=2))
        return
    
    # Default to text format
    if not issues:
        print("No issues found for this release.")
        return
    
    print(f"Found {len(issues)} issues:")
    print("-" * 120)
    print(f"{'Key':<15} {'Type':<15} {'Status':<15} {'Priority':<10} {'Summary'}")
    print("-" * 120)
    
    for issue in issues:
        key = issue.get("key", "N/A")
        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "N/A")
        status = issue.get("fields", {}).get("status", {}).get("name", "N/A")
        priority = issue.get("fields", {}).get("priority", {}).get("name", "N/A")
        summary = issue.get("fields", {}).get("summary", "N/A")
        
        # Truncate summary if it's too long
        if len(summary) > 70:
            summary = summary[:67] + "..."
        
        print(f"{key:<15} {issue_type:<15} {status:<15} {priority:<10} {summary}")


def display_versions(versions, output_format="text"):
    """
    Displays the versions in the specified format.
    
    Args:
        versions (list): List of version objects
        output_format (str): Output format ('text', 'json')
    """
    if output_format == "json":
        print(json.dumps(versions, indent=2))
        return
    
    # Default to text format
    if not versions:
        print("No releases found for this project.")
        return
    
    # Sort versions by release date (if available) or by name
    sorted_versions = sorted(
        versions,
        key=lambda v: v.get("releaseDate", "9999-99-99") if v.get("releaseDate") else "9999-99-99"
    )
    
    print(f"Found {len(versions)} releases:")
    print("-" * 80)
    print(f"{'ID':<10} {'Name':<20} {'Released':<10} {'Release Date':<12} {'Description'}")
    print("-" * 80)
    
    for version in sorted_versions:
        version_id = version.get("id", "N/A")
        name = version.get("name", "N/A")
        released = "Yes" if version.get("released", False) else "No"
        release_date = version.get("releaseDate", "N/A")
        description = version.get("description", "")
        
        print(f"{version_id:<10} {name:<20} {released:<10} {release_date:<12} {description}")


def main():
    parser = argparse.ArgumentParser(description="Extract and print all releases associated with a Jira project")
    parser.add_argument("project_key", help="Jira project key (e.g., PROJ)")
    parser.add_argument("--url", required=True, help="Jira base URL (e.g., https://your-domain.atlassian.net)")
    parser.add_argument("--user", required=True, help="Jira username or email")
    parser.add_argument("--token", required=True, help="Jira API token")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (text or json)")
    parser.add_argument("--release-id", help="Show issues for a specific release ID")
    parser.add_argument("--list-issues", action="store_true", help="List all issues for the specified release")
    
    args = parser.parse_args()
    
    # If release ID is specified and list-issues flag is set, show issues for that release
    if args.release_id and args.list_issues:
        issues = get_issues_for_version(args.url, args.project_key, args.release_id, args.user, args.token)
        display_issues(issues, args.format)
    # Otherwise, just show all releases
    else:
        versions = get_project_versions(args.url, args.project_key, args.user, args.token)
        display_versions(versions, args.format)


if __name__ == "__main__":
    main()
