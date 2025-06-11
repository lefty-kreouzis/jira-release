# Jira Releases Extractor

A Python script to extract and print all releases associated with a Jira project.

## Prerequisites

- Python 3.6 or higher
- Jira account with API access
- Jira API token (can be generated from your Atlassian account)

## Installation

1. Clone this repository or download the script.
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
./jira_releases.py PROJECT_KEY --url JIRA_URL --user JIRA_USERNAME --token JIRA_API_TOKEN [--format FORMAT] [--release-id RELEASE_ID --list-issues]
```

### Arguments:

- `PROJECT_KEY`: The Jira project key (e.g., PROJ)
- `--url`: Base URL of your Jira instance (e.g., https://your-domain.atlassian.net)
- `--user`: Your Jira username or email
- `--token`: Your Jira API token
- `--format`: Output format (text or json), default is text
- `--release-id`: ID of a specific release to show issues for
- `--list-issues`: Flag to list all issues for the specified release ID

### Examples:

```bash
# List all releases for a project
./jira_releases.py MYPROJECT --url https://my-company.atlassian.net --user user@example.com --token abc123xyz456

# List all releases in JSON format
./jira_releases.py MYPROJECT --url https://my-company.atlassian.net --user user@example.com --token abc123xyz456 --format json

# List all issues for a specific release
./jira_releases.py MYPROJECT --url https://my-company.atlassian.net --user user@example.com --token abc123xyz456 --release-id 10001 --list-issues
```

## Getting a Jira API Token

1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give your token a name (e.g., "Release Script")
4. Click "Create" and copy the token

## Output Examples

### Text Format (Default) - Releases
```
Found 3 releases:
--------------------------------------------------------------------------------
ID         Name                 Released    Release Date Description
--------------------------------------------------------------------------------
10001      v1.0.0              Yes         2023-05-15   Initial release
10002      v1.1.0              Yes         2023-07-20   Feature update
10003      v2.0.0              No          N/A          Major version release
```

### Text Format - Issues for a Release
```
Found 5 issues:
------------------------------------------------------------------------------------------------------------------------
Key            Type            Status          Priority   Summary
------------------------------------------------------------------------------------------------------------------------
PROJ-123       Bug             Resolved        High       Fix authentication issue in login form
PROJ-124       Story           Closed          Medium     Add user profile page
PROJ-125       Task            Done            Low        Update documentation for v1.0.0
PROJ-126       Improvement     Resolved        Medium     Optimize database queries for better performance
PROJ-127       Bug             Closed          Critical   Fix security vulnerability in password reset
```

### JSON Format
```json
[
  {
    "id": "10001",
    "name": "v1.0.0",
    "released": true,
    "releaseDate": "2023-05-15",
    "description": "Initial release"
  },
  ...
]
```
