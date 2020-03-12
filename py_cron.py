import datetime
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from croniter import croniter

# currently set to deal with time.sleep() max input
MAX_WAIT = 2760000

# print lock, to prevent multiple threads printing concurrently
print_lock = threading.Lock()


def import_pctab(args):
    """Exports schedule table file, as Path object ie. pctab.txt."""
    import argparse

    parser = argparse.ArgumentParser(
        description="""Cron-style task scheduler.
        """
    )
    parser.add_argument(
        "pctab",
        help="""File containing scheduling table.
            """,
        type=str,
    )

    return Path(parser.parse_args(args).pctab)


def parse_pctab(pctab_file):
    """Returns the schedule table as a list formatted [date-and-time, [task args]]"""
    with pctab_file.open() as f:
        pctab_ = f.readlines()

    pctab = [[" ".join(line.split()[:5]), line.split()[5:]] for line in pctab_]

    return pctab


def time_left(next):
    """Calculates seconds from now till datetime."""
    timedelta = next - datetime.datetime.now()
    return timedelta.total_seconds()


def run_task(task):
    """Runs the task through a subprocess call.
    subprocess.Popen() is non-blocking, and can be polled if we want to get a returncode, etc.
    """

    s_print("Running {}.".format(task))
    try:
        subprocess.Popen(
            task,
            stdout=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.realpath(__file__)),
            shell=True,
        )
    except OSError as e:
        s_print("Execution failed:", e, file=sys.stderr)

    return True


def start_tasks(pctab):
    """Starts threads for each task in pctab."""
    tasks = []

    for schedule, task in pctab:
        job = Job(schedule, task)
        job.start()
        tasks.append(job)

    return tasks


def end_tasks(tasks):
    """Stops all threads. Not being used, as threads are set as daemons."""
    for job in tasks:
        job.stop()


class Job(threading.Thread):
    def __init__(self, schedule, task):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stopped = False
        self.schedule = schedule
        self.task = task

    def stop(self):
        self.stopped = True
        self.join()

    def run(self):
        try:
            s_print("Thread started for {} {}.".format(self.schedule, self.task))
            base = datetime.datetime.now()
            iter = croniter(self.schedule, base)

            while not self.stopped:
                next_runtime = iter.get_next(datetime.datetime)
                wait_time = time_left(next_runtime)
                s_print(
                    "Task {} next scheduled for {}.".format(self.task, next_runtime)
                )

                while wait_time > MAX_WAIT:
                    time.sleep(MAX_WAIT)
                    wait_time -= MAX_WAIT

                time.sleep(wait_time)

                run_task(self.task)
        finally:
            s_print("Thread ended for {} {}.".format(self.schedule, self.task))


def s_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


if __name__ == "__main__":
    pctab_file = import_pctab(sys.argv[1:])
    pctab = parse_pctab(pctab_file)
    try:
        tasks = start_tasks(pctab)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        s_print("Scheduler Finished.")
