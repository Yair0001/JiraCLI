from jira import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import RequestException
import questionary
from rich.console import Console

# Initialize the console for rich output
console = Console()

def get_credentials():
    console.print("[bold cyan]Please enter your Jira credentials:[/bold cyan]")

    jira_server = questionary.text(
        "Jira server URL (e.g. https://your-domain.atlassian.net):"
    ).ask()

    jira_email = questionary.text(
        "Your Jira email:"
    ).ask()

    jira_token = questionary.password(
        "Your Jira API token (input hidden):"
    ).ask()

    return jira_server, jira_email, jira_token

def get_jira_client():
    while True:
        try:
            jira_server, jira_email, jira_token = get_credentials()

            jira = JIRA(
                server=jira_server,
                basic_auth=(jira_email, jira_token)
            )

            user = jira.current_user()
            console.print(f"[bold green]✅ Connected to Jira as {user}[/bold green]")
            return jira
        except JIRAError as e:
            if e.status_code == 401:
                console.print("[bold red]❌ Authentication failed. Check your email and API token.[/bold red]")
            elif e.status_code == 403:
                console.print("[bold red]❌ Forbidden. You may not have permission to access Jira.[/bold red]")
            elif e.status_code == 404:
                console.print("[bold red]❌ Invalid Jira URL. Check the domain and try again.[/bold red]")
            else:
                console.print(f"[bold red]❌ JIRAError: {e.text or str(e)}[/bold red]")

        except RequestException as e:
            console.print(f"[bold red]❌ Network error: {e}. Check your internet or Jira URL.[/bold red]")

        except Exception as e:
            console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")

        retry = questionary.confirm("[bold yellow]Would you like to try again?[/bold yellow]").ask()
        if not retry:
            return None
