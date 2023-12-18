@echo !) Run the commands below after run `.\venv\Scripts\activate`

@echo Stopping the Savant...
docker stop rabbitmq

@echo Starting the Savant...
start "Savant"     docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
timeout /t 12

@echo Starting the side-servers of aide...
start "Appearance" uvicorn kins.main:appearance --factory --reload --port 12001
start "Brain"      uvicorn kins.main:brain      --factory --reload --port 12002
start "Keeper"     uvicorn kins.main:keeper     --factory --reload --port 12003

@echo All servers started.
