```bash
docker build -f Dockerfile -t ade-scheduler .
docker run --name ade-scheduler -it -v $HOME/Documents/ADE-Scheduler:/ADE-Scheduler ade-scheduler
docker start -i ade-scheduler       # To run the app
docker exec -it ade-scheduler zsh   # To e.g. run `flask shell`
```