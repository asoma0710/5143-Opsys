import time
class Scheduler:
    """
    Handles the scheduling logic, including FCFS, RR, PB, and MLFQ.
    Tracks job statistics (ST, TAT, RWT, IWT) and calculates final metrics.
    """

    def __init__(self, num_cpus, num_ios, time_slice=None, algorithm="FCFS", mlfq_config=None):
        """
        Initialize the scheduler.
        :param num_cpus: Number of CPUs in the system.
        :param num_ios: Number of I/O devices in the system.
        :param time_slice: Time slice for RR or MLFQ.
        :param algorithm: Selected scheduling algorithm ("FCFS", "RR", "PB", "MLFQ").
        :param mlfq_config: Configuration for MLFQ (queues and time slices).
        """
        self.num_cpus = num_cpus
        self.num_ios = num_ios
        self.cpus = [{"id": i, "job": None, "remaining_time": 0, "time_used": 0} for i in range(num_cpus)]
        self.ios = [{"id": i, "job": None, "remaining_time": 0} for i in range(num_ios)]
        self.total_time = 0
        self.cpu_busy_time = 0
        self.io_busy_time = 0
        self.time_slice = time_slice
        self.algorithm = algorithm
        self.mlfq_queues = mlfq_config.get("queues", []) if mlfq_config else None
        self.mlfq_time_slices = mlfq_config.get("time_slices", []) if mlfq_config else None
        
    def run(self, queues, session_id, job_manager):
        """
        Execute the chosen scheduling algorithm.
        """
        if self.algorithm == "FCFS":
            self.run_fcfs(queues)
        elif self.algorithm == "RR":
            self.run_rr(queues)
        elif self.algorithm == "PB":
            self.run_pb(queues)
        elif self.algorithm == "MLFQ":
            self.run_mlfq(queues)
        else:
            raise ValueError(f"Unsupported scheduling algorithm: {self.algorithm}")
    def clean_empty_burst_jobs(self, queues):
        """
        Remove jobs with no remaining bursts from all queues and terminate them.
        """
        for queue_name, queue in queues.items():
            if queue_name not in ["Terminated"]:  # Skip terminated queue
                for job in list(queue):  # Use list to avoid modification issues
                    if not job.bursts:
                        print(f"At t:{self.total_time}, job {job.job_id} in {queue_name} terminated due to no remaining bursts.")
                        queue.remove(job)
                        self.terminate_job(job, queues)


    def move_new_to_ready(self, queues, clock):
        """
        Move jobs from the New queue to the Ready queue based on arrival time.
        """
        ready_jobs = [job for job in queues["New"] if job.arrival_time+1 == clock]
        for job in ready_jobs:
            queues["New"].remove(job)
            queues["Ready"].append(job)
            self.mlfq_queues[0].append(job)  # Place job in the highest-priority queue

            print(f"At t:{clock} job p{job.job_id} moved from New to Ready queue.")

    def assign_jobs_to_cpus(self, queues):
        """
        Assign jobs from the Ready queue to available CPUs only if the first burst type is 'CPU'.
        Handle jobs with 'EXIT' burst type immediately.
        """
        print("queues when came to cpus", queues)

        for cpu in self.cpus:
            if cpu["job"] is None:  # Only assign if the CPU is idle
                # Look for a job in the Ready queue
                job_to_assign = None
                for job in queues["Ready"]:
                    # Handle jobs with 'EXIT' burst type
                    if job.bursts and job.bursts[0].burst_type == "EXIT":
                        print(f"At t:{self.total_time}, job {job.job_id} has EXIT burst type and will be terminated.")
                        queues["Ready"].remove(job)
                        self.terminate_job(job, queues)
                        continue

                    # Check if the first remaining burst is 'CPU'
                    if job.bursts and job.bursts[0].burst_type == "CPU":
                        job_to_assign = job
                        break

                if job_to_assign:
                    queues["Ready"].remove(job_to_assign)  # Remove the job from the Ready queue
                    cpu["job"] = job_to_assign  # Assign the job to the CPU
                    cpu["remaining_time"] = job_to_assign.bursts[0].duration  # Set burst duration
                    queues["Running"].append(job_to_assign)  # Move the job to the Running queue
                    print(f"At t:{self.total_time}, job p{job_to_assign.job_id} obtained CPU:{cpu['id']}")
                else:
                    # No jobs with a 'CPU' burst as the first burst; CPU remains idle
                    print(f"At t:{self.total_time} CPU:{cpu['id']} remains idle as no eligible job is found.")


    def assign_jobs_to_ios(self, queues):
        """
        Assign jobs from the Waiting queue to available I/O devices if their first burst type is 'IO'.
        Handle jobs with 'EXIT' burst type immediately.
        """
        print("queues when came to ios", queues)

        for io in self.ios:
            if io["job"] is None:  # Only assign if the I/O device is idle
                # Look for a job in the Waiting queue
                job_to_assign = None
                for job in queues["Waiting"]:
                    # Handle jobs with 'EXIT' burst type
                    if job.bursts and job.bursts[0].burst_type == "EXIT":
                        print(f"At t:{self.total_time}, job {job.job_id} has EXIT burst type and will be terminated.")
                        queues["Waiting"].remove(job)
                        self.terminate_job(job, queues)
                        continue

                    # Check if the first remaining burst is 'IO'
                    if job.bursts and job.bursts[0].burst_type == "IO":
                        job_to_assign = job
                        break

                if job_to_assign:
                    io["job"] = job_to_assign  # Assign the job to the I/O device
                    queues["Waiting"].remove(job_to_assign)  # Remove the job from the Waiting queue
                    io["remaining_time"] = job_to_assign.bursts[0].duration  # Set burst duration
                    queues["Io"].append(job_to_assign)  # Move the job to the Io queue
                    print(f"At t:{self.total_time}, job p{job_to_assign.job_id} assigned to IO:{io['id']} for burst duration {job_to_assign.bursts[0].duration}")
                else:
                    # No jobs with an 'IO' burst as the first burst; I/O remains idle
                    print(f"At t:{self.total_time} IO:{io['id']} remains idle as no eligible job is found.")




    def run_rr(self, queues):
        """
        Round-Robin scheduling algorithm for both CPU and I/O devices.
        """
        # Increment the total time
        self.total_time += 1

        # Assign jobs to CPUs and I/O devices
        self.assign_jobs_to_cpus(queues)
        self.assign_jobs_to_ios(queues)

        # Update CPU states
        for cpu in self.cpus:
            if cpu["job"]:
                cpu["remaining_time"] -= 1
                cpu["time_used"] += 1
                self.cpu_busy_time += 1
                job = cpu["job"]
                job.bursts[0].duration -= 1
                
                if job.bursts[0].duration == 0:  # Burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Running"].remove(job)
                    cpu["job"] = None
                    cpu["time_used"] = 0
                elif cpu["time_used"] >= self.time_slice:  # Time slice exhausted
                    queues["Ready"].append(job)
                    queues["Running"].remove(job)
                    cpu["job"] = None
                    cpu["time_used"] = 0
                    

        # Update I/O states
        for io in self.ios:
            if io["job"]:
                
                time.sleep(5)
                io["remaining_time"] -= 1
                self.io_busy_time += 1
                job = io["job"]
                job.bursts[0].duration -= 1

                if job.bursts[0].duration == 0:  # I/O burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Io"].remove(job)
                    io["job"] = None


    def run_pb(self, queues):
        """
        Preemptive Priority-Based scheduling algorithm for both CPU and I/O devices.
        """
        # Increment the total time
        self.total_time += 1

        # Sort the Ready queue based on priority (lower number is higher priority)
        queues["Ready"].sort(key=lambda job: job.priority)

        # Check for preemption in CPUs
        for cpu in self.cpus:
            if cpu["job"]:  # If a job is running
                current_job = cpu["job"]
                if queues["Ready"] and queues["Ready"][0].priority < current_job.priority:
                    # Preempt the current job
                    queues["Ready"].append(current_job)  # Move the current job back to the Ready queue
                    queues["Running"].remove(current_job)  # Remove it from the Running queue
                    cpu["job"] = None  # Free the CPU
                    print(f"At t:{self.total_time}, job {current_job.job_id} preempted by job {queues['Ready'][0].job_id}.")

        # Assign jobs to CPUs and I/O devices
        self.clean_empty_burst_jobs(queues)  # Ensure no invalid jobs are in the queues
        self.assign_jobs_to_cpus(queues)
        self.assign_jobs_to_ios(queues)

        # Update CPU states
        for cpu in self.cpus:
            if cpu["job"]:
                cpu["remaining_time"] -= 1
                self.cpu_busy_time += 1
                job = cpu["job"]
                job.bursts[0].duration -= 1

                if job.bursts[0].duration == 0:  # Burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Running"].remove(job)
                    cpu["job"] = None

        # Update I/O states
        for io in self.ios:
            if io["job"]:
                io["remaining_time"] -= 1
                self.io_busy_time += 1
                job = io["job"]
                job.bursts[0].duration -= 1

                if job.bursts[0].duration == 0:  # I/O burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Io"].remove(job)
                    io["job"] = None


        
    def run_fcfs(self, queues):
        """
        First-Come, First-Served scheduling algorithm for both CPU and I/O devices.
        """
        # Increment the total time
        self.total_time += 1

        # Assign jobs to CPUs and I/O devices
        self.assign_jobs_to_cpus(queues)
        self.assign_jobs_to_ios(queues)

        # Update CPU states
        for cpu in self.cpus:
            if cpu["job"]:
                cpu["remaining_time"] -= 1
                self.cpu_busy_time += 1
                job = cpu["job"]
                job.bursts[0].duration -= 1

                if job.bursts[0].duration == 0:  # Burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Running"].remove(job)
                    cpu["job"] = None

        # Update I/O states
        for io in self.ios:
            if io["job"]:
                io["remaining_time"] -= 1
                self.io_busy_time += 1
                job = io["job"]
                job.bursts[0].duration -= 1

                if job.bursts[0].duration == 0:  # I/O burst finished
                    job.bursts.pop(0)
                    if not job.bursts:  # No more bursts; terminate the job
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                        queues["Waiting"].append(job)
                    else:  # Move back to Ready queue
                        queues["Ready"].append(job)
                    queues["Io"].remove(job)
                    io["job"] = None
                    
    def run_mlfq(self, queues):
        """
        Multi-Level Feedback Queue (MLFQ) scheduling algorithm for both CPU and I/O devices.
        """
        # Increment the total time
        self.total_time += 1

        # Aging Mechanism: Promote long-waiting jobs periodically to prevent starvation
        if self.total_time % 50 == 0:  # Example aging interval
            for level in range(1, len(self.mlfq_queues)):
                for job in list(self.mlfq_queues[level]):  # Use a list copy to avoid iteration issues
                    if self.total_time - job.arrival_time >= 100:  # Example threshold for aging
                        self.mlfq_queues[level].remove(job)
                        self.mlfq_queues[max(level - 1, 0)].append(job)
                        print(f"At t:{self.total_time}, job {job.job_id} aged to Level {max(level - 1, 0)}.")

        # Iterate over MLFQ levels (highest priority first)
        for level, queue in enumerate(self.mlfq_queues):
            for cpu in self.cpus:
                # Assign jobs to idle CPUs
                if cpu["job"] is None and queue:
                    job = queue.pop(0)
                    cpu["job"] = job
                    cpu["remaining_time"] = min(self.mlfq_time_slices[level], job.bursts[0].duration)
                    cpu["time_used"] = 0
                    queues["Running"].append(job)
                    print(f"At t:{self.total_time}, job {job.job_id} assigned to CPU {cpu['id']} at Level {level}")

                # Update running jobs on the CPU
                if cpu["job"]:
                    cpu["remaining_time"] -= 1
                    cpu["time_used"] += 1
                    self.cpu_busy_time += 1
                    job = cpu["job"]
                    job.bursts[0].duration -= 1

                    # Handle burst completion
                    if job.bursts[0].duration == 0:
                        job.bursts.pop(0)
                        queues["Running"].remove(job)
                        cpu["job"] = None  # Free the CPU

                        if not job.bursts:  # Job finished
                            self.terminate_job(job, queues)
                        elif job.bursts[0].burst_type == "IO":  # Move to Waiting queue
                            queues["Waiting"].append(job)
                            print(f"At t:{self.total_time}, job {job.job_id} moved to Waiting queue for I/O.")
                        else:  # Return to highest priority or same queue
                            self.mlfq_queues[max(level - 1, 0)].append(job)
                            print(f"At t:{self.total_time}, job {job.job_id} returned to Level {max(level - 1, 0)}.")

                    # Handle time slice expiration
                    elif cpu["time_used"] >= self.mlfq_time_slices[level]:
                        next_level = min(level + 1, len(self.mlfq_queues) - 1)
                        queues["Running"].remove(job)
                        self.mlfq_queues[next_level].append(job)
                        cpu["job"] = None  # Free the CPU
                        print(f"At t:{self.total_time}, job {job.job_id} demoted to Level {next_level}.")

        # Process Waiting queue and assign I/O devices
        for io in self.ios:
            if io["job"] is None:  # Assign waiting jobs to idle I/O devices
                for job in queues["Waiting"]:
                    if job.bursts and job.bursts[0].burst_type == "IO":
                        queues["Waiting"].remove(job)
                        io["job"] = job
                        io["remaining_time"] = job.bursts[0].duration
                        queues["Io"].append(job)
                        print(f"At t:{self.total_time}, job {job.job_id} assigned to IO:{io['id']} for duration {job.bursts[0].duration}.")
                        break

            # Update I/O jobs
            if io["job"]:
                io["remaining_time"] -= 1
                self.io_busy_time += 1
                job = io["job"]
                job.bursts[0].duration -= 1

                # Handle I/O completion
                if job.bursts[0].duration == 0:
                    job.bursts.pop(0)
                    queues["Io"].remove(job)
                    io["job"] = None  # Free the I/O device

                    if not job.bursts:
                        self.terminate_job(job, queues)
                    elif job.bursts[0].burst_type == "IO":
                        queues["Waiting"].append(job)
                    else:
                        self.mlfq_queues[0].append(job)  # Move to highest-priority queue
                        print(f"At t:{self.total_time}, job {job.job_id} moved to Level 0 after I/O.")

        # Log the longest waiting time for jobs in Level 2 (lowest priority)
        if len(self.mlfq_queues) > 2:
            longest_waiting_level3 = max(
                (self.total_time - job.arrival_time for job in self.mlfq_queues[2]), default=0
            )
            print(f"At t:{self.total_time}, Longest Waiting Time in Level 3: {longest_waiting_level3}")






    def terminate_job(self, job, queues):
        """
        Terminate a job and display its statistics upon completion.
        """
        job.terminated_time = self.total_time  # Set the termination time
        job.turnaround_time = job.terminated_time - job.arrival_time  # Calculate Turnaround Time (TAT)
        job.ready_wait_time = job.ready_wait_time  # Time spent in READY queue (already tracked)
        job.io_wait_time = job.io_wait_time  # Time spent in WAIT queue (already tracked)

        # Print the job statistics
        print(f"At t:{self.total_time} job p{job.job_id} terminated. "
            f"ST={job.arrival_time}, TAT={job.turnaround_time}, "
            f"RWT={job.ready_wait_time}, IWT={job.io_wait_time}")

        # Append the job to the terminated queue
        queues["Terminated"].append(job)
