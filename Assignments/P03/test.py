import requests
import json 
import os
from rich import print  # Import rich for better console printing with colors and styles

# Function to create the configuration for the session
def getConfig(client_id):
    return {
        "client_id": client_id,  # Unique identifier for the client
        "min_jobs": 5,  # Minimum number of jobs to generate
        "max_jobs": 20,  # Maximum number of jobs to generate
        "min_bursts": 10,  # Minimum bursts for each job
        "max_bursts": 50,  # Maximum bursts for each job
        "min_job_interval": 1,  # Minimum time between job arrivals
        "max_job_interval": 5,  # Maximum time between job arrivals
        "burst_type_ratio": 0.5,  # Ratio of CPU to I/O bursts
        "min_cpu_burst_interval": 15,  # Minimum duration for CPU bursts
        "max_cpu_burst_interval": 50,  # Maximum duration for CPU bursts
        "min_io_burst_interval": 30,  # Minimum duration for I/O bursts
        "max_io_burst_interval": 70,  # Maximum duration for I/O bursts
        "min_ts_interval": 5,  # Minimum time slice for jobs
        "max_ts_interval": 5,  # Maximum time slice for jobs
        "priority_levels": [1, 2, 3, 4, 5]  # List of priority levels
    }

# Function to initialize the simulation
def init(config):
    """
    This function will initialize the client and return the `client_id` and `session_id`
    """
    route = f"http://profgriffin.com:8000/init"  # API endpoint for initialization
    r = requests.post(route, json=config)  # Send a POST request with the configuration
    if r.status_code == 200:  # If the response is successful
        response = r.json()  # Parse the response as JSON
        return response  # Return the parsed response
    else:
        print(f"Error: {r.status_code}")  # Print an error message if the request fails
        return None  # Return None if there was an error

# Function to get new jobs at the current clock time
def getJob(client_id, session_id, clock_time):  
    route = f"http://profgriffin.com:8000/job?client_id={client_id}&session_id={session_id}&clock_time={clock_time}"  # API endpoint
    r = requests.get(route)  # Send a GET request
    if r.status_code == 200:  # If the response is successful
        response = r.json()  # Parse the response as JSON
        return response  # Return the parsed response
    else:
        print(f"Error: {r.status_code}")  # Print an error message if the request fails
        return None  # Return None if there was an error

# Function to get the next burst for a specific job
def getBurst(client_id, session_id, job_id):
    route = f"http://profgriffin.com:8000/burst?client_id={client_id}&session_id={session_id}&job_id={job_id}"  # API endpoint
    r = requests.get(route)  # Send a GET request
    if r.status_code == 200:  # If the response is successful
        response = r.json()  # Parse the response as JSON
        return response  # Return the parsed response
    else:
        print(f"Error: {r.status_code}")  # Print an error message if the request fails
        return None  # Return None if there was an error

# Function to check how many bursts are left for a specific job
def getBurstsLeft(client_id, session_id, job_id):
    route = f"http://profgriffin.com:8000/burstsLeft?client_id={client_id}&session_id={session_id}&job_id={job_id}"  # API endpoint
    r = requests.get(route)  # Send a GET request
    if r.status_code == 200:  # If the response is successful
        response = r.json()  # Parse the response as JSON
        return response  # Return the parsed response
    else:
        print(f"Error: {r.status_code}")  # Print an error message if the request fails
        return None  # Return None if there was an error

# Function to check how many jobs are left in the session
def getJobsLeft(client_id, session_id):
    route = f"http://profgriffin.com:8000/jobsLeft?client_id={client_id}&session_id={session_id}"  # API endpoint
    r = requests.get(route)  # Send a GET request
    if r.status_code == 200:  # If the response is successful
        response = r.json()  # Parse the response as JSON
        return response  # Return the parsed response
    else:
        print(f"Error: {r.status_code}")  # Print an error message if the request fails
        return None  # Return None if there was an error

# Main execution block
if __name__ == '__main__':
    do_init = False  # Flag for initialization (not used in the code)
    do_job = False  # Flag for job fetching (not used in the code)
    do_burst = False  # Flag for burst fetching (not used in the code)

    jobs = {}  # Dictionary to store job details

    client_id = "sgtrock"  # Unique client identifier
    config = getConfig(client_id)  # Get the configuration for the client
    
    print("configuration is",config)
    base_url = 'http://profgriffin.com:8000/'  # Base URL for API
    response = init(config)  # Initialize the session
    
    print("response is :",response)
    print(response)  #Print the initialization response

    start_clock = response['start_clock']  # Get the starting clock time
    session_id = response['session_id']  # Get the session ID

    clock = start_clock  # Set the clock to the starting time

    while(clock):  # Main loop
        jobsLeft = getJobsLeft(client_id, session_id)  # Check how many jobs are left
        if not jobsLeft:  # If no jobs are left, terminate the loop
            break
        response = getJob(client_id, session_id, clock)  # Fetch new jobs at the current clock time
        if response and response['success']:  # If the response is successful and contains data
            if response['data']:  # If there are new jobs
                for data in response['data']:  # Iterate over the new jobs
                    job_id = data['job_id']  # Get the job ID
                    print(f"Job {job_id} received at {clock}...")  # Log the received job
                    if job_id not in jobs:  # If the job is not already in the dictionary
                        jobs[job_id] = {'data': data, 'bursts': {}}  # Add the job to the dictionary

        print(jobs)  # Print the current jobs dictionary

        for job_id in jobs:  # Iterate over all jobs
            burstsLeft = getBurstsLeft(client_id, session_id, job_id)  # Check how many bursts are left for the job
            if not burstsLeft:  # If no bursts are left, log and continue
                print(f"No bursts left for job {job_id} at {clock}")
                continue
            bresp = getBurst(client_id, session_id, job_id)  # Fetch the next burst for the job
            if isinstance(bresp, dict) and 'success' in bresp and bresp['success']:  # If the burst fetch is successful
                burst = bresp['data']  # Get the burst data
                bid = burst['burst_id']  # Get the burst ID
                print(f"Burst {bid} received ...")  # Log the received burst
                jobs[job_id]['bursts'][bid] = burst  # Add the burst to the job's data

        clock += 1  # Increment the clock
