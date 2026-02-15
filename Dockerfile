FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume for persistent data
VOLUME ["/app/data"]

# Environment variables (override at runtime)
ENV CORAL_AGENT_ID=research_assistant
ENV CORAL_AGENT_DESCRIPTION="Research assistant agent for Coral Protocol"
ENV PYTHONUNBUFFERED=1

# Run the MCP server (for Coral integration)
# or use CMD ["python", "research_agent.py"] for standalone mode
CMD ["python", "research_mcp_server.py"]
