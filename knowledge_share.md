# Setting up and Using cqljupyter: A Complete Guide

This guide will walk you through setting up cqljupyter, a Jupyter kernel for Apache Cassandra, from scratch. We'll cover everything from environment setup to running your first CQL queries.

## Prerequisites

- Python 3.x installed on your system
- Docker installed on your system
- Basic understanding of Jupyter notebooks
- Basic understanding of Cassandra/CQL

## Step 1: Set Up Python Environment

First, let's set up a clean Python environment:

```bash
# Create a new directory for your project
mkdir cqljupyter_project
cd cqljupyter_project

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

## Step 2: Install cqljupyter

With your virtual environment activated, install cqljupyter:

```bash
pip install cqljupyter
```

## Step 3: Install Docker

1. Visit [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Download and install Docker Desktop for your operating system
3. Start Docker Desktop
4. Verify installation:
```bash
docker --version
```

If you get a "command not found" error, you need to add Docker to your system PATH:

### For macOS/Linux:
```bash
# Add Docker to PATH
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"

# To make it permanent, add the above line to your shell profile:
# For bash: ~/.bashrc or ~/.bash_profile
# For zsh: ~/.zshrc
```

### For Windows:
1. Open System Properties (Win + Pause/Break)
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find and select "Path"
5. Click "Edit"
6. Click "New"
7. Add the Docker installation path (typically `C:\Program Files\Docker\Docker\resources\bin`)
8. Click "OK" on all windows
9. Restart your terminal

After adding Docker to PATH, restart your terminal and try `docker --version` again.

## Step 4: Set Up DataStax Enterprise (DSE) Server

1. Pull the DSE Server Docker image:
```bash
docker pull datastax/dse-server:5.1.48-ubi7
```

## Step 5: Start DSE Server

Run the DSE Server container:

```bash
docker run -d \
  --name dse \
  -p 9042:9042 \
  -e DS_LICENSE=accept \
  datastax/dse-server:5.1.48-ubi7
```

Wait for the container to fully start. You can monitor the startup in two ways:

1. Check container status:
```bash
docker ps
```

2. Monitor the container logs until you see "DSE startup complete":
```bash
docker logs -f dse
```

The `-f` flag will follow the logs in real-time. You can press Ctrl+C to stop watching the logs once you see the completion message.

## Step 6: Configure cqljupyter

Configure cqljupyter to connect to your local DSE instance:

```bash
python -m cqljupyter.install localhost 9042
```

Note: If you need authentication, use:
```bash
python -m cqljupyter.install localhost 9042 -u username -p password
```

> **Important**: You can run this configuration command at any time to update your connection settings. This is useful when:
> - Changing the connection host or port
> - Adding or modifying authentication credentials
> - Switching between different DSE instances
> 
> After running the configuration command, it's recommended to restart Jupyter Notebook for the changes to take effect.

## Step 7: Start Jupyter Notebook

1. First, verify if Jupyter Notebook is installed:
```bash
jupyter --version
```

If you get a "command not found" error, install Jupyter Notebook:
```bash
pip install notebook
```

2. Start Jupyter Notebook:
```bash
jupyter notebook
```

3. In the Jupyter interface:
   - Click "New" in the top right
   - Select "CQL" from the kernel options

## Step 8: Running CQL Queries

Here's a sample notebook to get you started:

```sql
-- Create a keyspace
CREATE KEYSPACE IF NOT EXISTS test_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Use the keyspace
USE test_keyspace;

-- Create a table
CREATE TABLE IF NOT EXISTS users (
    user_id uuid PRIMARY KEY,
    name text,
    email text
);

-- Insert data
INSERT INTO users (user_id, name, email)
VALUES (uuid(), 'John Doe', 'john@example.com');

-- Query data
SELECT * FROM users;
```

## Tips and Best Practices

1. **Auto-completion**: Use the TAB key to invoke auto-complete in your CQL cells
2. **HTML Output**: Start a cell with `%%html` to render HTML content
3. **Connection Issues**: If you experience connection problems:
   - Ensure Docker is running
   - Check if the DSE container is healthy: `docker ps`
   - Verify the connection settings in your cqljupyter configuration
4. **Jupyter Hub**: To use with Jupyter Hub:
   - Install cqljupyter in your Jupyter Hub environment
   - Configure the kernel in your Jupyter Hub setup
   - Ensure the DSE server is accessible from your Jupyter Hub environment

## Troubleshooting

1. **Kernel Not Found**:
   - Restart Jupyter Notebook
   - Verify cqljupyter installation: `pip list | grep cqljupyter`

2. **Connection Errors**:
   - Check Docker container status
   - Verify port 9042 is accessible
   - Ensure correct host and port in cqljupyter configuration

3. **Docker Issues**:
   - Restart Docker Desktop
   - Check Docker logs: `docker logs dse`

## Additional Resources

- [cqljupyter GitHub Repository](https://github.com/bradschoening/cqljupyter)
- [DataStax Enterprise Documentation](https://docs.datastax.com/en/dse/6.8/dse-dev/datastax_enterprise/index.html)
- [Jupyter Documentation](https://jupyter.org/documentation)
- [Apache Cassandra Documentation](https://cassandra.apache.org/doc/latest/) 