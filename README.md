# Jira Issue Management CLI Tool

A command-line interface tool for interacting with Jira, built with Python.

## Overview

This Jira Issue Management CLI Tool provides a user-friendly interface to interact with your Jira instance directly from the terminal. It helps you perform common Jira operations without leaving your command line environment.

## Features

- **Authentication**: Secure connection to your Jira instance using API tokens
- **Issue Management**:
  - Get detailed information about specific issues
  - Create new issues with custom fields
  - List issues with flexible filtering options
  - Update existing issues
  - Delete issues
- **Rich Console Output**: Color-coded and formatted output for better readability
- **Interactive Interface**: User-friendly prompts for input

## Requirements

- Docker installed on your system
- Jira API credentials (email and API token)
- Jira instance URL

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/jira-cli.git
   cd jira-cli
   ```

2. Build:
   ```
   docker build -t jira-cli .
   ```

## Usage

Run the docker build:
```
docker run -it --rm jira-cli
```

### Available Actions

After authenticating, you can choose from the following actions:

1. **Get an Issue**: Retrieve and display detailed information about a specific issue
2. **Create an Issue**: Create a new issue with customizable fields
3. **List Issues**: Display issues from a project with optional filtering by type and status
4. **Update an Issue**: Modify field values of an existing issue
5. **Delete an Issue**: Remove an issue from Jira (requires confirmation)
6. **Exit**: Close the application

## Project Structure

- `main.py`: Entry point containing the main application logic and command handlers
- `jira_client.py`: Handles authentication and connection to the Jira API
- `utils.py`: Utility functions for formatting output and handling API data
- `issue_actions.py`: Handles all the different issue actions