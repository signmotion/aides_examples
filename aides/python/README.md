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
poetry install
```

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

See `*/kins/savant/README.md`.
