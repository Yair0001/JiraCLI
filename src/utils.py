from termcolor import colored

def print_issue(issue):
    print(f"\nProject: {issue.fields.project}")
    print(f"{colored('Issue Key:', 'yellow')} {colored(issue.key, 'cyan')}")
    print(f"{colored('Summary:', 'yellow')} {colored(issue.fields.summary, 'cyan')}")
    print(f"{colored('Status:', 'yellow')} {colored(issue.fields.status.name, 'cyan')}")
    print(f"{colored('Reporter:', 'yellow')} {colored(issue.fields.reporter.displayName, 'cyan')}")
    print(f"{colored('Creator:', 'yellow')} {colored(issue.fields.creator.displayName, 'cyan')}")
    print(f"{colored('Priority:', 'yellow')} {colored(issue.fields.priority.name, 'cyan')}")
    print(f"{colored('Duedate:', 'yellow')} {colored(issue.fields.duedate, 'cyan')}")
    print(f"{colored('Description:', 'yellow')} {colored(issue.fields.description if issue.fields.description else 'No description available', 'cyan')}")


def get_create_metadata(jira, project_key):
    try:
        # Get the create metadata for a specific project
        url = f"{jira._options['server']}/rest/api/2/issue/createmeta"
        params = {'projectKeys': project_key, 'expand': 'projects.issuetypes.fields'}
        response = jira._session.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching create metadata: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching create metadata: {e}")
        return None