# Buy on eBay

The servers for appraise purchase the items on eBay.

Developed for A\*.

They are in the folders:

- appearance
- brain
- keeper
- savant

## Run

Work into the PowerShell or Bash terminal. In VSCode bottom pane: open `PowerShell` or `Git Bash`.

Remember that all servers are independent.

### Install

Look at `README.md` into each server folder.

The common starts steps for all servers described below.

Move to the server folder and run commands below after that. For example:

```bash
cd kins/appearance
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

```bash
pip install -r requirements.txt
```

#### Note: Pipeline for Update Requirements

```bash
pip install NAME-PACKAGE
```

Look at package version into the console output or run in CMD into the current environment:

```bash
pip list
```

Add the package name with version to `requirements.txt`.

### Run Servers

See `README.md` into the servers folders.
