# Buy on eBay

The server for appraise purchase the items on eBay.

Powered by [Celery & FastAPI](https://testdriven.io/courses/fastapi-celery/getting-started/).

## Current state

!) Stopped. Reason: Have the error on the stage <https://testdriven.io/courses/fastapi-celery/app-factory/#H-10-manual-test>.

Celery is not officially supported on Windows, and some features may not work as expected.

## Run

Work into the Bash terminal. In VSCode bottom pane: open `Git Bash`.

Run the commands below in the root foolder.

### Install

See <https://testdriven.io/courses/fastapi-celery/getting-started>.

### Activate the virtual environment

#### Activate on Windows

```cmd
python -m venv venv
```

```cmd
.\venv\Scripts\activate
```

#### Linux

```cmd
source venv/bin/activate
```

### Install requirements

```cmd
pip install -r requirements.txt
```

### Install & run Redis

#### Install Redis on Windows

[How do run Redis on Windows?](https://stackoverflow.com/questions/6476945/how-do-i-run-redis-on-windows)

Start Ubuntu and typing:

```cmd
sudo apt-add-repository ppa:redislabs/redis
```

```cmd
sudo apt-get update
```

```cmd
sudo apt-get upgrade
```

```cmd
sudo apt-get install redis-server
```

```cmd
sudo service redis-server restart
```

Check installation:

```cmd
set user:1 "Andrii"
```

```cmd
get user:1
```

### Run Redis on Windows

Start Ubuntu.

```cmd
sudo service redis-server start
```

### Run Celery server

```cmd
celery -A main.celery worker --loglevel=info
```
