# Savant

The part of Aide.

Powered by RabbitMQ.

This server doesn't need to prepare environment: we use a Docker image.

Tested on Docker installation. See <https://rabbitmq.com/download.html>.

## Run This Server with Docker

```bash
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
```

### Check Queries

Start the commands below directly consider to [doc](https://docs.docker.com/engine/reference/commandline/exec/) or run Docker Shell from own CMD:

```bash
docker exec -it rabbitmq sh
```

Or use `Exec` tab into the Docker Desktop.

```bash
rabbitmqctl list_queues
```
