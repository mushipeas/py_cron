# `py_cron`

A cron-style task scheduler with python.

Written for and tested on Python 3.7.6, on Windows.

## To Initialise the Project

### Recommended:
In the root dir of project, run:

    python -m venv .venv
This should create a virtual environment

### Activate the environment:
    .\.venv\Scripts\activate (Windows)
    source .venv/bin/activate (UNIX)

### Install required packages:
    pip install -r requirements.txt


## Running from cmd-line:

### Usage
    usage: py_cron.py [-h] pctab

    Cron-style task scheduler.

    positional arguments:
        pctab       File containing scheduling table.

    optional arguments:
        -h, --help  show this help message and exit.

### PCTAB Format
The program requires a table representing the tasks to be run and their timings.
This should be in the following format:

    * * * * * task1 -arg1 -arg2
    */10 * * * * task2 -arg


### Example
    python py_crontab.py pctab.txt 
