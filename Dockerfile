FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Make the run script executable
RUN chmod +x /app/run_scraper.sh

# Set the entry point
ENTRYPOINT ["/app/run_scraper.sh"]
