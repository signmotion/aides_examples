# Demo Examples for RabbitMQ

Examples from [RabbitMQ Get Started](https://rabbitmq.com/#getstarted).

## Run

Work into the PowerShell or Bash terminal. In VSCode bottom pane: open `PowerShell` or `Git Bash`.

Run the commands below in the root foolder.

### Install

Tested on Docker installation. See <https://rabbitmq.com/download.html>.

#### Run Docker Image

```cmd
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
```

### Activate the Virtual Environment

#### Activate on Windows

```cmd
python -m venv venv
```

```cmd
.\venv\Scripts\activate
```

##### Upgrade `pip`

Run into the global CMD:

```cmd
pip install --upgrade pip
```

### Install Requirements

```cmd
pip install -r requirements.txt
```

#### Pipeline for Update Requirement

```cmd
pip install NAME-PACKAGE
```

Look at package version into the console output or run in CMD into the current environment:

```cmd
pip list
```

Add the package name with version to `requirements.txt`.

### Run the First Demo

```cmd
python receive.py
```

In other CMD:

```cmd
python send.py
```

For work these programs you need to run the Docker image. See above.

### Check Queries

Use UI by address <http://localhost:15672>.

Or start the commands below directly consider to [doc](https://docs.docker.com/engine/reference/commandline/exec/).

Or run Docker Shell
from own CMD:

```cmd
docker exec -it rabbitmq sh
```

Or use `Exec` tab into the Docker Desktop.

```cmd
rabbitmqctl list_queues
```
