#!/bin/bash
set -e

# Check if GitHub username is provided
if [ -z "$1" ]; then
  echo "Please provide your GitHub username as the first argument"
  echo "Usage: ./push-to-github.sh <github_username> [repository_name]"
  exit 1
fi

GITHUB_USERNAME=$1

# Set repository name (default to current directory name if not provided)
if [ -z "$2" ]; then
  REPO_NAME=$(basename $(pwd))
else
  REPO_NAME=$2
fi

echo "Initializing Git repository..."
git init

echo "Adding files to Git..."
git add .

echo "Committing files..."
git commit -m "Initial commit"

echo "Creating GitHub repository: $REPO_NAME"
# This requires the GitHub CLI to be installed and authenticated
# If you don't have it, you can create the repository manually on GitHub
if command -v gh &> /dev/null; then
  gh repo create "$REPO_NAME" --public --confirm
else
  echo "GitHub CLI not found. Please create the repository manually on GitHub:"
  echo "https://github.com/new"
  echo ""
  echo "Then run the following commands:"
  echo "git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
  echo "git branch -M main"
  echo "git push -u origin main"
  exit 0
fi

echo "Adding GitHub remote..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "Setting main branch..."
git branch -M main

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Your repository is now available at: https://github.com/$GITHUB_USERNAME/$REPO_NAME" 