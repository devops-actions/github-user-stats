#!/usr/bin/env python3
"""
GitHub User Statistics Fetcher

This script fetches GitHub user activity statistics including pull requests,
issues, and discussions for a specified user within a given time period.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Any


class GitHubUserStats:
    """Class to fetch and display GitHub user statistics."""
    
    def __init__(self, token: str, username: str):
        """
        Initialize the GitHubUserStats instance.
        
        Args:
            token: GitHub personal access token
            username: GitHub username to fetch stats for
        """
        self.token = token
        self.username = username
        self.api_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def fetch_user_activity(self, days: int) -> Dict[str, Any]:
        """
        Fetch user activity for the specified number of days.
        
        Note: This fetches the most recent 100 items of each type. For very active users,
        some older items within the time period may not be included. Client-side filtering
        is used to match the specified time range.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary containing user statistics
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Note: GitHub's GraphQL API doesn't support filtering by date directly in the query
        # for user's pullRequests, issues, and discussions. We fetch recent items and filter
        # client-side. The limit of 100 per type should cover most use cases.
        query = """
        query($username: String!) {
          user(login: $username) {
            login
            name
            pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
              totalCount
              nodes {
                title
                createdAt
                url
                state
                repository {
                  nameWithOwner
                }
              }
            }
            issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
              totalCount
              nodes {
                title
                createdAt
                url
                state
                repository {
                  nameWithOwner
                }
              }
            }
            repositoryDiscussions(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
              totalCount
              nodes {
                title
                createdAt
                url
              }
            }
          }
        }
        """
        
        variables = {
            "username": self.username
        }
        
        response = requests.post(
            self.api_url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed with status {response.status_code}: {response.text}")
        
        data = response.json()
        
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        return self._process_data(data["data"]["user"], since_date, days)
    
    def _parse_github_datetime(self, date_string: str) -> datetime:
        """
        Parse GitHub's ISO 8601 datetime format.
        
        Args:
            date_string: ISO format datetime string from GitHub API
            
        Returns:
            datetime object
        """
        # GitHub returns ISO 8601 format with 'Z' suffix for UTC
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    
    def _process_data(self, user_data: Dict, since_date: str, days: int) -> Dict[str, Any]:
        """
        Process the raw API data and filter by date range.
        
        Args:
            user_data: Raw user data from GitHub API
            since_date: ISO format date string for filtering
            days: Number of days looked back
            
        Returns:
            Processed statistics dictionary
        """
        since_dt = self._parse_github_datetime(since_date)
        
        # Filter pull requests by date
        prs = [
            pr for pr in user_data["pullRequests"]["nodes"]
            if self._parse_github_datetime(pr["createdAt"]) >= since_dt
        ]
        
        # Filter issues by date
        issues = [
            issue for issue in user_data["issues"]["nodes"]
            if self._parse_github_datetime(issue["createdAt"]) >= since_dt
        ]
        
        # Filter discussions by date
        discussions = [
            disc for disc in user_data["repositoryDiscussions"]["nodes"]
            if self._parse_github_datetime(disc["createdAt"]) >= since_dt
        ]
        
        return {
            "username": user_data["login"],
            "name": user_data.get("name", "N/A"),
            "period_days": days,
            "since_date": since_date,
            "pull_requests": {
                "count": len(prs),
                "items": prs
            },
            "issues": {
                "count": len(issues),
                "items": issues
            },
            "discussions": {
                "count": len(discussions),
                "items": discussions
            }
        }
    
    def print_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Print formatted statistics to stdout.
        
        Args:
            stats: Statistics dictionary
        """
        print("\n" + "=" * 80)
        print(f"GitHub User Statistics for @{stats['username']}")
        if stats['name'] != "N/A":
            print(f"Name: {stats['name']}")
        print(f"Period: Last {stats['period_days']} days (since {stats['since_date'][:10]})")
        print("=" * 80)
        
        # Pull Requests
        print(f"\n📋 Pull Requests: {stats['pull_requests']['count']}")
        if stats['pull_requests']['items']:
            print("\nRecent Pull Requests:")
            for pr in stats['pull_requests']['items'][:10]:  # Show top 10
                state_emoji = "✅" if pr['state'] == "MERGED" else "🟢" if pr['state'] == "OPEN" else "❌"
                print(f"  {state_emoji} {pr['repository']['nameWithOwner']}")
                print(f"     {pr['title']}")
                print(f"     {pr['url']} ({pr['createdAt'][:10]})")
        
        # Issues
        print(f"\n🐛 Issues: {stats['issues']['count']}")
        if stats['issues']['items']:
            print("\nRecent Issues:")
            for issue in stats['issues']['items'][:10]:  # Show top 10
                state_emoji = "🟢" if issue['state'] == "OPEN" else "✅"
                print(f"  {state_emoji} {issue['repository']['nameWithOwner']}")
                print(f"     {issue['title']}")
                print(f"     {issue['url']} ({issue['createdAt'][:10]})")
        
        # Discussions
        print(f"\n💬 Discussions: {stats['discussions']['count']}")
        if stats['discussions']['items']:
            print("\nRecent Discussions:")
            for disc in stats['discussions']['items'][:10]:  # Show top 10
                print(f"  💬 {disc['title']}")
                print(f"     {disc['url']} ({disc['createdAt'][:10]})")
        
        # Summary
        print("\n" + "=" * 80)
        print("Summary:")
        print(f"  Total Activity Items: {stats['pull_requests']['count'] + stats['issues']['count'] + stats['discussions']['count']}")
        print("=" * 80 + "\n")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch GitHub user statistics for pull requests, issues, and discussions"
    )
    parser.add_argument(
        "--username",
        default="rajbos",
        help="GitHub username to fetch statistics for (default: rajbos)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)"
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (or use GITHUB_TOKEN environment variable)"
    )
    parser.add_argument(
        "--output-file",
        help="Optional: write the output to a file instead of stdout"
    )
    
    args = parser.parse_args()
    
    # Get token from args or environment
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token is required. Provide via --token or GITHUB_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize and fetch stats
        fetcher = GitHubUserStats(token, args.username)
        print(f"Fetching statistics for @{args.username} over the last {args.days} days...", file=sys.stderr)
        stats = fetcher.fetch_user_activity(args.days)
        
        # Redirect output if file is specified
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                # Temporarily redirect stdout
                original_stdout = sys.stdout
                sys.stdout = f
                fetcher.print_statistics(stats)
                sys.stdout = original_stdout
            print(f"✅ Statistics saved to {args.output_file}", file=sys.stderr)
        else:
            # Print results to stdout
            fetcher.print_statistics(stats)
            print("✅ Statistics fetched successfully!", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
