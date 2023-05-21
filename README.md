# NOTE
the README is outdated, working on it atm

# smart-surveillance-system
inspired by the chinese government.
btw will crash if you don't have an nvidia GPU...don't @ me

# Running
sit back and relax, it's gonna take a jiffy (again thx to nvidia)
## makefile
```bash
make docker-build
make docker-run
```

## no makefile
(yuck)
```bash
docker build -t face-rec-nvidia:latest .
docker run -p 8000:8000 --gpus all -it --rm face-rec-nvidia:latest
```

# Interacting
there are three endpoints for now (and probably in the foreseeable future)
## POST request
on `localhost:8000/docs` there is only one request that works without websockets (hint: it's the only one in the docs)

simply pass a person's image and their class (a class being a person's name, not their social standing)

if it replies with `{ok:true}` that means the person is detected, stored, and marked as supporter of the AI revolution

if it returns anything else then you're either trying to manually test the program (don't), or your computer is about to explode in a comically amusing manner

## websocket endpoints
there are two. they do the exact same thing

one is simply more efficient than the other, i just keep the other as a demonstration of my genius. 

the good one being `/blockstream/` which is used for videos

right now if you want to test this one out...you can't, a video has to be passed to it and god knows i will procrastinate making the WS client. (code donations are appreciated)
