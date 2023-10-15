# Pacayadb Viz


This repository aims to visualize the data from the pacayadb sensors

## Setup

### Docker

You need to have docker and docker compose installed from the web.

This brings up the db in detached mode.

`docker-compose up pacayadb -d`


### Python

Ensure all the packages you need are installed. Would recommend
using a virtualenv to set this up.

`pip install -r requirements.txt`


### SQL data

The sql data is private to the project and is restricted acces. If 
you need access to it, please reach out to me.


## Graphs

To bring up raw graphs with sensor ids, you can run

`python plot_graphs.py` in a virtualenv with the dependencies installed.

