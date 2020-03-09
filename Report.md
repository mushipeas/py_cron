Py_cron by Mujtaba Zaidi

Foreword:

If I was working on this project for myself, I would first find an existing solution for scheduling, ie. APScheduler, and either implement something around this, or use it as inspiration.
Using the APScheduler library for example, and parsing a crontab-style file into scheduled tasks on it, would be trivial. From a quick glance, it has cron commands which would allow near-direct conversion of a crontab file into scheduled tasks.
For the purposes of this exercise, however, I'll only be assessing the functionality of cron with crontab and trying to build a limited version of this in Python.


Thinking Process:

I initially thought of single-threaded solutions.
First, I could use a similar approach to cron, where the script checks for 'matches' against the time-and-date strings for all tasks every minute(using scheduler, to prevent time-drift). All that match the current minute are then called. My concern here was that if I'm looking for an efficient approach that uses the minimum cpu - the checks every minute (for many tasks I would assume may run every 60, 1440 or 86400 minutes, or far longer), there would be a lot of useless checks, and the efficiency of the application would heavily depend on the efficiency of the checking. Assuming I have limited time, I don't want to spend a great deal of time getting the one function super efficient.

A less cpu-intense process would have a parser that would determine all upcoming scheduled runtimes for all tasks in a lookahead window (ie. 24 hours), and create a sorted queue. These could then be added to a scheduler instance. The main loop would then sleep till just after the window, and then regenerate the queue and add scheduled tasks again.
However, I felt that it reduced possible future expandability in terms of task completion / run monitoring. It would also mean a larger overall memory load, and spikes in cpu useage every regeneration period. It would also require logic to avoid missing task runs which might coincide with the queue build. ie if the queue was set to be regenerated at 12:00 daily, and a task was scheduled for every 0'th minute of every hour.

Instead, I opted for a multi-threaded approach, where each task had its own call/sleep loop.
As each task runner would be spending most of its time waiting, I felt that using a multi-threaded approach would be easiest, as it would require the least complexity in terms of managing queues and sleep timers.
The threads would use a helper function to provide only the next upcoming runtime (croniter, in this case) for the given time-and-date string, and sleep accordingly. One concern here would be the maximum sleep time vs possible tasks far in the future. As such, if the next runtime is greater than X seconds, a reduced sleep time would be used in a loop. This would repeat until the task was closer than X seconds away. At the moment, it it set to 2760000s, or 31.94 days.
I used threads instead of processes to make logging easier.
Using a delay has a problem - in that if the device goes into sleep/hibernation, then the process calls would be delayed by the sleep time. This could be overcome by monitoring the system for sleep alerts from the OS, and restarting the threads in that situation.


Assumptions:

- Not using any existing task scheduling libraries.
- The script will run in the cmd-line, but is not a true service. ie. It does not register in the OS as a service, and does not run as a deamon or on startup.
- As a cron-style service, it will implement a similar cron-tab file format for setting up scheduling.


Limitations:

- Very limited error catching.
- As the script is not a true service, it cannot run on start-up without additional work, and cannot use "@reboot" as a command.
- Nonstandard commands and characters (@hourly, @yearly, /...) have not been implemented. However the code can easily be expanded to add such functionality.
- The script is currently run directly. Usually for a final product, I would make it installable using setup.py. However, this is trivial, and it would just add complication to the submitted code.
- The tasks will all run at the same privilege as the python script, and there is no ability to set this, or the user.
- There is no proper logging. At the moment, the script just writes to console.
- Tasks can only be added by changing the input file (pctab.txt) and re-running the script. There is no CLI.
- No multi-user / multi-privilege support.
- As we're using multi-threading, there's a theoretical maximum number of scheduled tasks. Multi-threading should still allow for hundreds of tasks. If thousands of tasks were being scheduled, I would resort to checking for matches every minute as mentioned above.
- Daylight savings has not been accounted for, so in some cases tasks could end up run twice, or at the wrong time just after daylight savings.
- No task success/failure checks. Will be fire and forget. This could be changed by polling the popen call.
- Limited tests for the threads / subprocess calls


Potential enhancements:

- Monitoring system for sleep/hibernate to restart schedules.
- Mocking the subprocess callout to do testing for the task runner function, using testfixtures.