#!/bin/bash
set -e

# Check for required environment variables
if [ -z "$AZURE_DEVOPS_PAT" ]; then
    echo "Error: AZURE_DEVOPS_PAT environment variable is not set"
    echo "Please set it with: export AZURE_DEVOPS_PAT='your-pat-token'"
    exit 1
fi

if [ -z "$AZURE_DEVOPS_ORG" ]; then
    echo "Error: AZURE_DEVOPS_ORG environment variable is not set"
    echo "Please set it with: export AZURE_DEVOPS_ORG='your-org-name'"
    exit 1
fi

# Install necessary dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y curl git jq

# Create agent directory
AGENT_DIR="$HOME/azagent"
mkdir -p "$AGENT_DIR"
cd "$AGENT_DIR"

# Download the agent
echo "Downloading Azure Pipelines agent..."
curl -O https://vstsagentpackage.azureedge.net/agent/3.234.0/vsts-agent-linux-x64-3.234.0.tar.gz

# Extract the agent
echo "Extracting agent package..."
tar zxvf vsts-agent-linux-x64-3.234.0.tar.gz

# Configure the agent
echo "Configuring agent..."
./config.sh --unattended \
  --agent "${HOSTNAME:-$(hostname)}" \
  --url "https://dev.azure.com/$AZURE_DEVOPS_ORG" \
  --auth pat \
  --token "$AZURE_DEVOPS_PAT" \
  --pool "Default" \
  --replace \
  --acceptTeeEula

# Install service
echo "Installing agent service..."
sudo ./svc.sh install

# Start the service
echo "Starting agent service..."
sudo ./svc.sh start

echo "Agent setup complete!" 