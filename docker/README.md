```bash
docker build -f Dockerfile -t ade-scheduler .
docker run --name ade-scheduler -it -p 5000:5000 -v <Path to ADE-Scheduler folder>:/ADE-Scheduler ade-scheduler
docker start -i ade-scheduler       # To run the app
docker exec -it ade-scheduler bash  # To e.g. run `flask shell`
```
