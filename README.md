


uvicorn sso_server.main:app --reload --host 0.0.0.0 --port 9000

docker run -p 27017:27017 --ip 0.0.0.0 mongo4.4