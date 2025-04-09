from utils import print_issue, get_create_metadata
import questionary
from jira.exceptions import JIRAError
import requests
from requests.exceptions import RequestException
from rich.console import Console
from rich.table import Table

console = Console()

def get_issue(jira):
    key = questionary.text("Enter issue key:").ask()
    try:
        issue = jira.issue(key)
        print_issue(issue)
    except JIRAError as e:
        # Handle JIRA-specific errors
        if e.status_code == 401:
            console.print("[bold red]❌ Unauthorized: Check your authentication details (API token or email).[/bold red]")
        elif e.status_code == 404:
            console.print(f"[bold red]❌ Issue with key {key} not found.[/bold red]")
        else:
            console.print(f"[bold red]❌ Jira error while fetching issue: {e.text}[/bold red]")
    except RequestException as e:
        # Handle network errors (e.g., timeout, no internet)
        console.print(f"[bold red]❌ Network error while fetching issue: {e}. Please check your internet connection.[/bold red]")
    except Exception as e:
        # Handle any unexpected errors
        console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")

def delete_issue(jira):
    # Prompt user for the issue key to delete
    issue_key = questionary.text("Enter the issue key to delete:").ask()
    if not issue_key:
        console.print("[bold yellow]Issue key cannot be empty.[/bold yellow]")
        return

    # Confirm deletion with the user to prevent accidental deletions
    confirm = questionary.confirm(f"Are you sure you want to delete the issue {issue_key}?").ask()
    if not confirm:
        console.print("[bold yellow]Issue deletion canceled.[/bold yellow]")
        return

    # Construct the URL to delete the issue
    url = f"{jira.server_url}/rest/api/2/issue/{issue_key}"

    try:
        # Send a DELETE request to the Jira API
        response = requests.delete(
            url,
            auth=(jira._session.auth[0], jira._session.auth[1]),  # Use stored authentication credentials
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            console.print(f"[bold green]Issue {issue_key} has been successfully deleted.[/bold green]")
        else:
            console.print(f"[bold red]Error deleting issue: {response.status_code} - {response.text}[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Unexpected error while deleting issue: {e}[/bold red]")

def list_issues(jira):
    try:
        # Ask user for project key
        project = questionary.text("Enter project key to list issues:").ask()
        if not project:
            console.print("[bold yellow]Project key cannot be empty.[/bold yellow]")
            return

        # Ask user for any filters (issue type or status)
        issue_type = questionary.select("Select issue type filter (optional):", choices=["All", "Bug", "Task", "Story", "Subtask"]).ask()
        status = questionary.select("Select status filter (optional):", choices=["All", "To Do", "In Progress", "Done"]).ask()

        # Construct JQL query based on user filters
        jql_query = f"project = {project}"

        if issue_type != "All":
            jql_query += f" AND issuetype = {issue_type}"

        if status != "All":
            jql_query += f" AND status = {status}"

        try:
            # Fetch issues using the constructed JQL query
            issues = jira.search_issues(jql_query, maxResults=20)  # Adjust maxResults as needed

            if not issues:
                console.print(f"[bold yellow]No issues found for the query: {jql_query}[/bold yellow]")
                return

            # Display issues in a rich table
            table = Table(title="Issues")
            table.add_column("Issue Key", style="bold cyan")
            table.add_column("Summary", style="bold magenta")
            table.add_column("Status", style="bold green")

            for issue in issues:
                table.add_row(issue.key, issue.fields.summary, issue.fields.status.name)
            
            console.print(table)

        except JIRAError as e:
            console.print(f"[bold red]JIRA API error: {e.status_code} - {e.text}[/bold red]")
            return
        except Exception as e:
            console.print(f"[bold red]Unexpected error while fetching issues: {e}[/bold red]")
            return

    except Exception as e:
        console.print(f"[bold red]Error in listing issues: {e}[/bold red]")

def update_issue(jira):
    key = questionary.text("Enter the issue key to update:").ask()

    try:
        # Fetch the existing issue by its key
        issue = jira.issue(key)

        # List all available fields (filter out system fields like reporter, created, updated)
        available_fields = [field for field in issue.fields.__dict__ if field not in ['reporter', 'created', 'updated', 'status', 'issuetype', 'project']]

        # Ask the user to choose which field they want to update
        field_to_update = questionary.text("Which field would you like to update? (Enter Exit to not update)").ask()

        if field_to_update == "Exit":
            console.print("[bold yellow]Exiting update process.[/bold yellow]")
            return
        elif field_to_update not in available_fields:
            console.print(f"[bold red]Invalid field selected. Available fields are: {', '.join(available_fields)}[/bold red]")
            return

        # Dynamically ask for the new value of the selected field
        new_value = questionary.text(f"Enter new value for '{field_to_update}' (current: {getattr(issue.fields, field_to_update)}):").ask()

        # Update the selected field with the new value
        if field_to_update in available_fields:
            try:
                issue.update(fields={field_to_update: new_value})
                console.print(f"[bold green]{field_to_update} updated successfully to: {new_value}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Error updating the field '{field_to_update}': {e}[/bold red]")
        else:
            console.print(f"[bold red]Invalid field selected: {field_to_update}[/bold red]")

        console.print(f"[bold green]Issue {key} updated successfully.[/bold green]")
        
    except JIRAError as e:
        console.print(f"[bold red]JIRA API error: {e.status_code} - {e.text}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

def create_issue(jira):
    project = questionary.text("Project key:").ask()

    # Fetch project metadata and issue types
    try:
        metadata = get_create_metadata(jira, project)
        if not metadata:
            console.print("[bold red]Unable to retrieve create metadata.[/bold red]")
            return
        
        # Get a list of issue type names for selection
        available_issue_types = []
        for project_metadata in metadata.get("projects", []):
            if project_metadata.get("key") == project:
                available_issue_types = [issue_type["name"] for issue_type in project_metadata.get("issuetypes", [])]

        # Ask user to select an issue type based on the available types for the project
        issue_type = questionary.select(
            "Issue type:",
            choices=available_issue_types
        ).ask()

        summary = questionary.text("Summary:").ask()
        description = questionary.text("Description:").ask()

        # Get the create metadata for the selected issue type
        fields_for_issue_type = {}
        for project_metadata in metadata.get("projects", []):
            if project_metadata.get("key") == project:
                for issue_type_metadata in project_metadata.get("issuetypes", []):
                    if issue_type_metadata.get("name") == issue_type:
                        fields_for_issue_type = issue_type_metadata.get("fields", {})
                        break

        excluded_fields = [
            "reporter", "assignee", "created", "updated", "issuetype",
            "project", "resolution", "resolutiondate", "issuetype", "summary", "description"
        ]
        # Dynamically check if any required fields are missing
        issue_fields = {
            'project': project,
            'summary': summary,
            'description': description,
            'issuetype': {"name": issue_type}
        }

        # Ask for custom fields
        for field_name, field_metadata in fields_for_issue_type.items():
            if field_metadata.get("required", False):
                if field_name not in excluded_fields:
                    if field_name == 'parent':
                        parent_key = questionary.text("Parent:").ask()
                        if parent_key:
                            issue_fields[field_name] = {"key": parent_key}
                    else:
                        field_value = questionary.text(f"{field_name.capitalize()}:").ask()
                        if field_value:
                            issue_fields[field_name] = field_value

        # Create the issue
        new_issue = jira.create_issue(fields=issue_fields)
        console.print(f"[bold green]✅ Issue created: {new_issue.key}[/bold green]")

    except JIRAError as e:
        console.print(f"[bold red]❌ JIRA error: {e.text}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")

if __name__ == "__main__":
    # Example usage of the functions
    pass
# This module is designed to handle various actions related to Jira issues.