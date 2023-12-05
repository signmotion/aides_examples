# Demo Examples for RabbitMQ & FastStream & FastAPI

The example from [there](https://faststream.airt.ai/latest/getting-started/integrations/fastapi).

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

### Install Requirements

```cmd
pip install -r requirements.txt
```

### Run the Demo

Producer server:

```cmd
uvicorn producer.main:app --reload
```

Consumer server:

```cmd
faststream run consumer.main:app --reload
```

For send messages from producer use the VSCode plugin `REST Client`.
See `test.http`.

!) For work these programs you need to run the Docker image. See above.

### Check Queries

Use RabbitMQ UI by address <http://localhost:15672>.

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
