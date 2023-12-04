# Buy on eBay

The server for appraise purchase the items on eBay.

Powered by [RabbitMQ](https://rabbitmq.com).

## Run

Work into the PowerShell or Bash terminal. In VSCode bottom pane: open `PowerShell` `Git Bash`.

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

### Send Message

```cmd
python main.py
```
