# Aides on the Python

## Conventions

### Structure

The servers able in the folder `*/kins`:

- appearance
- brain
- keeper
- savant

### Skip the verb for get- and set-functions

Exclude: `Context`.

---

## Run

The steps below are same for all Python's aides.

Work into the PowerShell or Bash terminal. In VSCode bottom pane: open `PowerShell` or `Git Bash`.

Remember that all servers are **independent**.

### Install

Look at `README.md` into each server folder.

The common starts steps for Python's projects described below.

Run commands below from the root project folder into PowerShell.

#### Install poetry

```bash
pip install pipx
```

```bash
pipx install poetry
```

For upgrade:

```bash
pipx upgrade poetry
```

### Activate the Virtual Environment

#### Activate on Windows

```bash
python -m venv venv
```

```bash
.\venv\Scripts\activate
```

### Install Requirements

Install requirements from poetry:

```bash
poetry install --no-root
```

or, when needed:

```bash
poetry lock
```

If the error appears after run the first command above then delete
the file `poetry.lock` and run the command again.

## Run Servers

### Run All Together

```bash
.\main_dev.bat
```

### Run Apart

#### Appearance

```bash
uvicorn kins.main:appearance --factory --reload --port 12001
```

#### Brain

```bash
uvicorn kins.main:brain --factory --reload --port 12002
```

#### Keeper

```bash
uvicorn kins.main:keeper --factory --reload --port 12003
```

#### Savant

This server doesn't need to prepare environment: we use a Docker image.

Tested on Docker installation. See <https://rabbitmq.com/download.html>.

##### Run This Server with Docker

```bash
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
```

###### Check Queries

Start the commands below directly consider to [doc](https://docs.docker.com/engine/reference/commandline/exec/)
or run Docker Shell from own CMD:

```bash
docker exec -it rabbitmq sh
```

Or use `Exec` tab into the Docker Desktop.

```bash
rabbitmqctl list_queues
```
