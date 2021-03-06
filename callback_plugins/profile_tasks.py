import time

from ansible import callbacks
from ansible.callbacks import display

class CallbackModule(object):
    """
    A plugin for timing tasks
    """
    def __init__(self):
        self.stats = {}
        self.current = None

    def playbook_on_task_start(self, name, is_conditional):
        """
        Logs the start of each task
        """
        if self.current is not None:
            # Record the running time of the last executed task
            self.stats[self.current] = time.time() - self.stats[self.current]

        # Record the start time of the current task
        self.current = name
        self.stats[self.current] = time.time()

    def playbook_on_stats(self, stats):
        """
        Prints the timings
        """
        display(callbacks.banner("PLAY TIMINGS"))

        # Record the timing of the very last task
        if self.current is not None:
            self.stats[self.current] = time.time() - self.stats[self.current]

        # the raw results
        results = self.stats.items()

        # Sort the tasks by their running time
        sortedResults = sorted(
            self.stats.items(),
            key=lambda value: value[1],
            reverse=True,
        )

        # Just keep the top 10
        sortedResults = sortedResults[:10]

        # the total time for all of the roles/tasks
        totalTime = 0;
        # the timings for the role
        roleTimings = {}

        # Print the timings
        for name, elapsed in results:
            # build up the role timings

            # first thing to do is to figure out whether it is a role
            strippedName = ""
            if (name.find("|") == -1):
              strippedName = "<NO_DEFINED_ROLE>"
            else:
              strippedName = name[:name.find("|")]

            if(strippedName in roleTimings):
                roleTimings[strippedName] = roleTimings[strippedName] + elapsed 
            else:
                roleTimings[strippedName] = elapsed

            print(
                "{0:-<70}{1:->9}".format(
                    '{0} '.format(name),
                    ' {0:.02f}s'.format(elapsed),
                )
            )
            totalTime = totalTime + elapsed

        # diaply the top 10 slowest tasks
        display(callbacks.banner("TOP 10 SLOWEST TASKS"))

        for name, elapsed in sortedResults:
            print(
                "{0:-<70}{1:->9}".format(
                    '{0} '.format(name),
                    ' {0:.02f}s'.format(elapsed),
                )
            )

        # Display the times per role
        display(callbacks.banner("ROLE TIMES"))
        for role, timing in sorted(roleTimings.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(
                "{0:-<70}{1:->9}".format(
                    '{0} '.format(role),
                    ' {0:.02f}s'.format(timing),
                )
            )

        # display the total time taken for the ansible job
        display(callbacks.banner("TOTAL TIME"))
        print(
            "{0:-<70}{1:>9}".format(
                '{0}'.format(""),
                ' {0:.02f}s'.format(totalTime),
            )
        )
