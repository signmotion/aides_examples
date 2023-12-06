# Buy on eBay

The server for appraise purchase the items on eBay.

Powered by [RabbitMQ](https://rabbitmq.com).

## Run

Work into the PowerShell or Bash terminal. In VSCode bottom pane: open `PowerShell` or `Git Bash`.

Run the commands below in the root foolder.

### Install

Tested on Docker installation. See <https://rabbitmq.com/download.html>.

#### Run Docker Image

```bash
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
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

#### Pipeline for Update Requirement

```bash
pip install NAME-PACKAGE
```

Look at package version into the console output or run in CMD into the current environment:

```bash
pip list
```

Add the package name with version to `requirements.txt`.

### Start Server

```bash
TBD
```

!) For work these commands correctly you need to run the Docker image. See above.

### Check Queries

Use RabbitMQ UI by address <http://localhost:15672>.

Or start the commands below directly consider to [doc](https://docs.docker.com/engine/reference/commandline/exec/).

Or run Docker Shell
from own CMD:

```bash
docker exec -it rabbitmq sh
```

Or use `Exec` tab into the Docker Desktop.

```bash
rabbitmqctl list_queues
```
