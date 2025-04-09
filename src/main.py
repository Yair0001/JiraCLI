from jira_client import get_jira_client
import questionary
from rich.console import Console

from issue_actions import (
    get_issue,
    create_issue,
    list_issues,
    update_issue,
    delete_issue,
)

console = Console()

def main():
    jira = get_jira_client()
    if not jira:
        return

    while True:
        choice = questionary.select(
            "Choose an action:", 
            choices=["Get an Issue", "Create an Issue", "List Issues", "Update an Issue", "Delete an Issue", "Exit"]
        ).ask()

        if choice == "Get an Issue":
            get_issue(jira)
        elif choice == "Create an Issue":
            create_issue(jira)
        elif choice == "List Issues":
            list_issues(jira)
        elif choice == "Update an Issue":
            update_issue(jira)
        elif choice == "Delete an Issue":
            delete_issue(jira)
        elif choice == "Exit":
            console.print("[bold blue]Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    main()
