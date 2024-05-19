import subprocess # Allow to handle input and output
import time

# Wait that both database are initialize. Fallback as docker is alreat doing this in docker-compose.yaml
def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False

# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting ELT script...")


# We start defining the source database config
source_config = {
    'db_name' : 'source_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'source_postgres' # Name of the service we put inside the docker compose file
}

# We start defining the deftination database config

destination_config = {
    'db_name' : 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'destination_postgres' # Name of the service we put inside the docker compose file
}

# We need to initialize the dump command to initialize the source dv

dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d',source_config['db_name'],
    '-f', 'data_dump.sql',
    '-w'
]

# We set the env variable to avoid the password any time

subprocess_env = dict(PGPASSWORD=source_config['password'])

# We run the dump command that will dump everything into the source

subprocess.run(dump_command, env=subprocess_env, check=True)

# Now we need to get everything from the source db to the destination

# Load command

load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['db_name'],
    '-a','-f', 'data_dump.sql',
    '-w'
]

# We set the env variable to avoid the password any time

subprocess_env = dict(PGPASSWORD=destination_config['password'])

# We need to execute the load command

subprocess.run(load_command,env=subprocess_env, check=True)

print("Ending ETL script")