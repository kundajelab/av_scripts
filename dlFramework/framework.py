scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import argparse;
import dlFramework;

def startMaster(options):

    #get a thing that can kick off a job given some arguments.
    #get a thing that will generate next job to kick off.
    #when it is kicked off, 



    
    kickoffStategy = getKickoffStrategy(options);
    jobMonitors = [];
    nextJob = kickoffStrategy.getNextJob();
    while (nextJob is not None):
        jobMonitor = nextJob.kickoff();
        jobMonitors.append(jobMonitor);
        nextJob = kickoffStrategy.getNextJob();

    #keep polling the job monitors to see if termination happened.
    for jobMonitor in jobMonitors:
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--config", help="Configuration yaml file", required=True);
    args = parser.parse_args();
    
    startMaster(args); 
