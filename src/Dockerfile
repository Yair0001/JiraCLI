FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py jira_client.py utils.py issue_actions.py ./

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]