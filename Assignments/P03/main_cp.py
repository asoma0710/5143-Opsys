import os
import time
import sys
import json
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
    status: Literal["NEW", "READY", "RUN", "WAIT", "TERMINATED"] = "NEW"
    ready_wait_time: int = 0  # Time spent in READY queue
    io_wait_time: int = 0  # Time spent waiting for I/O
    run_time: int = 0  # Time spent running
    terminated: bool = False  # Whether the job is terminated


def fetch_bursts(job_manager: JobManager, session_id: int, job_id: int) -> List[BurstDetail]:
    """
    Fetch the full list of bursts for a given job by making API calls until an 'EXIT' burst is encountered.

    Args:
        job_manager (JobManager): Instance of JobManager to fetch bursts.
        session_id (int): Session ID for the API call.
        job_id (int): Job ID for which to fetch bursts.

    Returns:
        List[BurstDetail]: A complete list of BurstDetail objects for the job.
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



def fetch_jobs(job_manager: JobManager, session_id: int, clock_time: int) -> List[JobDetails]:
    """
    Fetch new jobs from the JobManager and convert them into JobDetails objects, including their full bursts list.

    Args:
        job_manager (JobManager): Instance of JobManager to fetch jobs.
        session_id (int): Current session ID.
        clock_time (int): Current simulation clock time.

    Returns:
        List[JobDetails]: A list of JobDetails objects with their full bursts list.
    """
    # Retrieve raw job data from the job manager
    raw_jobs = job_manager.get_new_jobs(session_id, clock_time)

    # Transform raw job data into JobDetails objects
    job_details_list = []
    for raw_job in raw_jobs:
        # Fetch bursts for this job
        bursts = fetch_bursts(job_manager, session_id, raw_job["job_id"])

        # Create the JobDetails object
        job = JobDetails(
            job_id=raw_job["job_id"],
            arrival_time=raw_job["arrival_time"],
            priority=raw_job.get("priority"),  # Include priority if available
            bursts=bursts
        )
        job_details_list.append(job)

    # Return the processed list of JobDetails
    return job_details_list


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


def main():
    """
    Main entry point for the CPU scheduling simulation.
    """
    # Process command-line arguments
    kwargs, args = myKwargs(sys.argv[1:])
    print(f"kwargs: {kwargs}")
    print(f"args: {args}")

    # Determine the configuration file path
    json_path = kwargs.get("config", "myConfig.json")  # Default to "myConfig.json"

    # Load configuration from JSON
    config = load_config(json_path)

    # Extract seed from kwargs or config
    seed = kwargs.get("seed", config.get("seed"))
    if seed is None:
        raise ValueError("A seed value must be provided either in the config file or as a command-line argument.")

    # Print configurations separately for verification
    print(f"Final Configuration (from JSON): {config}")
    print(f"Command-Line Arguments: {kwargs}")
    print(f"Using seed: {seed}")

    # Initialize Job Manager and Scheduler
    client_id = config["client_id"]
    print("\nClient ID is ", client_id) 
    job_manager = JobManager(config)

    # Pass the seed to init_simulation
    start_clock, session_id,time_slice = job_manager.init_simulation(seed=seed)

    # Determine scheduler configuration (use JSON config + kwargs)
    scheduler_algorithm = kwargs.get("sched", config.get("sched", "FCFS"))
    num_cpus = kwargs.get("cpus", 1)
    num_ios = kwargs.get("ios", 1)


    scheduler = Scheduler(
        num_cpus=num_cpus,
        num_ios=num_ios,
        time_slice=time_slice, 
        algorithm=scheduler_algorithm,
        mlfq_config=config.get("mlfq_config", {
            "queues": [[], [], []],
            "time_slices": [5, 10, 20],
        }),
    )

    # Initialize job queues
    queues = {
        "New": [],
        "Ready": [],
        "Running": [],
        "Waiting": [],
        "Terminated": [],
    }
    
    max_jobs=config.get("max_bursts")
    time_interval=config.get("max_job_interval")
    

    # jobs=fetch_jobs(job_manager,session_id,start_clock+max_jobs*time_interval)
    

    
    # print("total jobs are :",jobs)
    
    
    # time.sleep(5)

    clock = start_clock  # Simulation clock

    while True:
        print(f"Current Clock Tick: {clock}")

        # Fetch new jobs and process
        new_jobs = job_manager.get_new_jobs(session_id, clock)
        if new_jobs:
            print(f"Fetched {len(new_jobs)} new job(s) at clock {clock}: {new_jobs}")

        # Add burst details and keep jobs in New queue for this tick
        for job in new_jobs:
            bursts = job_manager.fetch_bursts(session_id, job["job_id"])
            if bursts:
                job["bursts"] = bursts
                queues["New"].append(job)
                print(f"Added Job {job['job_id']} to New queue with bursts: {bursts}")
            else:
                print(f"Job {job['job_id']} has no bursts and will be ignored.")

        # Transition jobs from New to Ready queue
        scheduler.move_new_to_ready(queues, clock)

        # Schedule jobs and update states
        scheduler.run(queues, session_id, job_manager)

        # Visualize all system states
        visualize_all(queues, scheduler.cpus, scheduler, clock)

        clock += 1
        time.sleep(1)

        # Exit condition
        if not job_manager.jobs_left(session_id) and not queues["Ready"] and not queues["New"] and not queues["Running"] and not queues["Waiting"]:
            break

    print("Simulation completed successfully.")


if __name__ == "__main__":
    main()
