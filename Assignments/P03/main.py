import os
import time
import sys
import json
import signal
from job_manager import JobManager
from scheduler import Scheduler
from visualization import visualize_all
from pydantic import BaseModel
from typing import List, Literal, Optional


class BurstDetail(BaseModel):
    burst_id: int
    burst_type: Literal["CPU", "IO", "EXIT"]
    duration: int  # Duration in milliseconds


class JobDetails(BaseModel):
    job_id: int
    arrival_time: int  # Time when the job arrives
    bursts: List[BurstDetail] = []  # Initialize with an empty list
    priority: Optional[int] = None  # Include priority from the API response
    ready_wait_time: int = 0  # Time spent in READY queue
    io_wait_time: int = 0  # Time spent waiting for I/O
    run_time: int = 0  # Time spent running
    time_in_queue: int = 0  # Time spent in the current queue mlfq only
    terminated: bool = False  # Whether the job is terminated
    terminated_time: Optional[int] = None  # Termination time, optional initially
    turnaround_time: Optional[int] = None  # Add the new field



def fetch_bursts_incrementally(job_manager: JobManager, session_id: int, job_id: int) -> List[BurstDetail]:
    """
    Fetch the full list of bursts for a given job incrementally until an 'EXIT' burst is encountered.
    """
    bursts = []
    while True:
        # Fetch bursts from the API
        burst_data = job_manager.fetch_bursts(session_id, job_id)

        # Convert raw burst data to BurstDetail objects
        for burst in burst_data:
            burst_detail = BurstDetail(
                burst_id=burst["burst_id"],
                burst_type=burst["burst_type"],
                duration=burst["duration"]
            )
            bursts.append(burst_detail)

            # Stop fetching if 'EXIT' burst is encountered
            if burst_detail.burst_type == "EXIT":
                return bursts


def fetch_unique_jobs(job_manager: JobManager, session_id: int, clock: int, queues: dict) -> List[JobDetails]:
    """
    Fetch new jobs from the JobManager, ensuring no duplicates are added to the queues.
    """
    # Fetch new jobs from the API
    new_jobs_data = job_manager.get_new_jobs(session_id, clock)

    unique_jobs = []
    for raw_job in new_jobs_data:
        # Check if the job is already in any queue
        if not any(job.job_id == raw_job["job_id"] for queue in queues.values() for job in queue):
            # Fetch bursts for the job
            bursts = fetch_bursts_incrementally(job_manager, session_id, raw_job["job_id"])

            # Create and return the new JobDetails object
            new_job = JobDetails(
                job_id=raw_job["job_id"],
                arrival_time=raw_job["arrival_time"],
                priority=raw_job.get("priority"),
                bursts=bursts
            )
            unique_jobs.append(new_job)
            print(f"\nAdded Job {new_job.job_id} to New queue\n")
        else:
            print(f"\nJob {raw_job['job_id']} is already present in the queues; skipping.\n")

    return unique_jobs


def myKwargs(argv):
    """
    Process command-line arguments into a dictionary (kwargs) and list (args).
    """
    kwargs = {}
    args = []
    for param in argv:
        if '=' in param:
            k, v = param.split('=')
            if v.isnumeric():
                kwargs[k] = int(v)
            else:
                kwargs[k] = v
        else:
            if param.isnumeric():
                param = int(param)
            args.append(param)

    return kwargs, args


def load_config(json_path):
    """
    Load configuration from a JSON file.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Configuration file not found: {json_path}")
    with open(json_path, 'r') as f:
        return json.load(f)

pid = os.getpid()

with open("out.txt", "w") as f:
    f.write(f"PID: {pid}\n")



# Global variable to control the simulation state
infinite_loop = False

def sigusr1_handler(signum, frame):
    """
    Signal handler for SIGUSR1: Toggles the infinite loop on or off.
    """
    global infinite_loop
    infinite_loop = not infinite_loop  # Toggle the state



def main():
    """
    Main entry point for the CPU scheduling simulation.
    """
    

    # Process command-line arguments
    kwargs, args = myKwargs(sys.argv[1:])
    print(f"\nkwargs: {kwargs}\n")
    print(f"\nargs: {args}\n")
    signal.signal(signal.SIGUSR1, sigusr1_handler)

    # Determine the configuration file path
    json_path = kwargs.get("config", "myConfig.json")  # Default to "myConfig.json"

    # Load configuration from JSON
    config = load_config(json_path)

    # Extract seed from kwargs or config
    seed = kwargs.get("seed", config.get("seed"))
    if seed is None:
        raise ValueError("A seed value must be provided either in the config file or as a command-line argument.")

    # # Print configurations separately for verification
    # print(f"\nFinal Configuration (from JSON): {config}\n")
    # print(f"\nCommand-Line Arguments: {kwargs}\n")
    # print(f"\nUsing seed: {seed}\n")

    # Initialize Job Manager and Scheduler
    client_id = config["client_id"]
    print("\nClient ID is ", client_id)
    print("\n")
    job_manager = JobManager(config)

    # Pass the seed to init_simulation
    start_clock, session_id, time_slice = job_manager.init_simulation(seed=seed)
    
    print("\ntime slice is ",time_slice,"\n")

    # Determine scheduler configuration (use JSON config + kwargs)
    scheduler_algorithm = kwargs.get("sched", config.get("sched", "FCFS"))
    num_cpus = kwargs.get("cpus", 1)
    num_ios = kwargs.get("ios", 1)


    # Simulation clock
    clock = start_clock

    scheduler = Scheduler(
        num_cpus=num_cpus,
        num_ios=num_ios,
        time_slice=time_slice,
        algorithm=scheduler_algorithm,
        mlfq_config=config.get("mlfq_config", {
            "queues": [[], [], []],
            "time_slices": [7, 10, 20],
        }),
    )

    # Initialize job queues
    queues = {
        "New": [],
        "Ready": [],
        "Running": [],
        "Waiting": [],
        "Io":[],
        "Terminated": [],
    }

    while True:
        print(f"\nCurrent Clock Tick: {clock}\n")

        # Fetch unique jobs and add them to the "New" queue
        new_jobs = fetch_unique_jobs(job_manager, session_id, clock, queues)
        queues["New"].extend(new_jobs)
        

        # Transition jobs from New to Ready queue
        scheduler.move_new_to_ready(queues, clock)
        
        if scheduler.algorithm != "MLFQ":
            for job in queues["Ready"]:
             job.ready_wait_time += 1
        
        for job in queues["Waiting"]:
            job.io_wait_time    +=1
        
        for job in queues["Running"]:
            job.run_time +=1

        # Schedule jobs and update states
        scheduler.run(queues, session_id, job_manager,clock)
        if infinite_loop:
            print("\nSIGUSR1 received: Entering infinite loop mode...wanna get out give me another interrupt\n")
            while infinite_loop:
                time.sleep(1)
        else:
            print("\nSIGUSR1 received: Exiting infinite loop mode...\n")
            time.sleep(1)        # Visualize all system states
        visualize_all(queues, scheduler.cpus, scheduler.ios, scheduler, clock, final=False)
        



        clock += 1

        # Exit condition
        if not job_manager.jobs_left(session_id) and not queues["Ready"] and not queues["New"] and not queues["Running"] and not queues["Waiting"] and not queues["Io"]:
            visualize_all(queues, scheduler.cpus, scheduler.ios, scheduler, clock, final=True)

            break

    print("\nSimulation completed successfully.\n")


if __name__ == "__main__":
    main()
