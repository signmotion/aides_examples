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

Server (consumer):

```cmd
uvicorn main:app --factory --reload
```

For send messages from Client (producer) use the VSCode plugin `REST Client`.
See `test.http`.

!) For work these programs you need to run the Docker image. See above.

### Check Queries

Start the commands below directly consider to [doc](https://docs.docker.com/engine/reference/commandline/exec/) or run Docker Shell from own CMD:

```cmd
docker exec -it rabbitmq sh
```

Or use `Exec` tab into the Docker Desktop.

```cmd
rabbitmqctl list_queues
```
