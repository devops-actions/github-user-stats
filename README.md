# GitHub User Statistics

A Python-based tool to fetch and analyze GitHub user activity statistics, including pull requests, issues, and discussions. The tool can be run locally or automated via GitHub Actions.

## Features

- 📊 Fetch comprehensive user activity statistics from GitHub
- 🔄 Configurable lookback period (days)
- 📋 Track pull requests, issues, and discussions
- 🤖 GitHub Actions workflow for automation
- 📝 Detailed activity reports
- 💾 Export results as artifacts

## Prerequisites

- Python 3.11 or higher
- GitHub Personal Access Token (PAT) with appropriate scopes:
  - `repo` (for private repositories)
  - `read:user` (for user data)
  - `read:discussion` (for discussions)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/devops-actions/github-user-stats.git
cd github-user-stats
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Local Execution

Run the script with default settings (user: `rajbos`, lookback: 30 days):

```bash
export GITHUB_TOKEN=your_github_token_here
python fetch_user_stats.py
```

### Custom Parameters

Specify a different user and lookback period:

```bash
python fetch_user_stats.py --username octocat --days 90
```

Or provide the token directly:

```bash
python fetch_user_stats.py --username rajbos --days 7 --token your_token_here
```

### Command-Line Options

- `--username`: GitHub username to fetch statistics for (default: `rajbos`)
- `--days`: Number of days to look back (default: `30`)
- `--token`: GitHub personal access token (alternatively, use `GITHUB_TOKEN` environment variable)
- `--output-file`: Optional path to write the output to a file instead of stdout

### Save Output to File

Save the statistics report to a file:

```bash
python fetch_user_stats.py --username rajbos --days 30 --output-file report.txt
```


## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that automatically fetches user statistics.

### Triggers

The workflow runs:
- **Manually**: Via workflow dispatch in the Actions tab
- **Scheduled**: Weekly on Mondays at 9 AM UTC
- **On Push**: When the script or workflow files are modified

### Manual Workflow Run

1. Go to the **Actions** tab in your GitHub repository
2. Select the "GitHub User Statistics" workflow
3. Click "Run workflow"
4. Optionally specify:
   - Username to analyze (default: `rajbos`)
   - Number of days to look back (default: `30`)

### Workflow Outputs

The workflow:
1. Displays statistics in the GitHub Actions logs
2. Generates a detailed report file
3. Uploads the report as an artifact (retained for 30 days)

### Download Artifacts

After a workflow run completes:
1. Go to the workflow run summary page
2. Scroll to the "Artifacts" section
3. Download `user-statistics-report` to view the detailed results

## Example Output

```
================================================================================
GitHub User Statistics for @rajbos
Name: Rob Bos
Period: Last 30 days (since 2025-11-20)
================================================================================

📋 Pull Requests: 15

Recent Pull Requests:
  ✅ devops-actions/load-used-actions
     Update dependency versions
     https://github.com/devops-actions/load-used-actions/pull/123 (2025-12-15)
  🟢 devops-actions/github-user-stats
     Add new statistics feature
     https://github.com/devops-actions/github-user-stats/pull/5 (2025-12-10)

🐛 Issues: 8

Recent Issues:
  🟢 devops-actions/marketplace-checks
     Enhancement: Add support for new action types
     https://github.com/devops-actions/marketplace-checks/issues/45 (2025-12-18)

💬 Discussions: 3

Recent Discussions:
  💬 Best practices for GitHub Actions security
     https://github.com/community/discussions/67890 (2025-12-12)

================================================================================
Summary:
  Total Activity Items: 26
================================================================================
```

## Security Considerations

- Never commit your GitHub token to the repository
- Use GitHub Secrets for storing tokens in workflows
- The default `GITHUB_TOKEN` provided by GitHub Actions has appropriate permissions for public repositories
- For private repositories, you may need to create a PAT with additional scopes

## Configuration

### GitHub Actions Secrets

The workflow uses `secrets.GITHUB_TOKEN`, which is automatically provided by GitHub Actions. No additional configuration is needed for public repositories.

For enhanced permissions or private repositories, create a PAT and add it as a secret named `GITHUB_TOKEN` in your repository settings.

## Customization

### Modify the Lookback Period

Edit the default value in the workflow file (`.github/workflows/user-stats.yml`):

```yaml
inputs:
  days:
    description: 'Number of days to look back'
    required: false
    default: '30'  # Change this value
```

### Change the Default User

Update the default username in the workflow file:

```yaml
inputs:
  username:
    description: 'GitHub username to analyze'
    required: false
    default: 'rajbos'  # Change this value
```

## Troubleshooting

### Authentication Errors

If you encounter authentication errors:
- Verify your token has the required scopes
- Check that the token hasn't expired
- Ensure the `GITHUB_TOKEN` environment variable is set correctly

### Rate Limiting

GitHub API has rate limits:
- Authenticated requests: 5,000 requests per hour
- The script uses GraphQL API which is more efficient
- If you hit rate limits, wait before retrying or reduce the lookback period

### No Data Returned

If no activity is found:
- Verify the username is correct
- Check if there's activity in the specified time period
- Ensure the token has access to view the user's activity

### Data Limitations

The script fetches the most recent 100 items of each type (pull requests, issues, discussions):
- For very active users, some older items within the time period may not be included
- This is a limitation of the GitHub GraphQL API query structure
- The 100-item limit per type typically covers most use cases
- If you need complete historical data, consider reducing the lookback period

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Maintained by [DevOps Actions](https://github.com/devops-actions)
