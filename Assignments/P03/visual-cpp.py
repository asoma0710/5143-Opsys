def visualize_all(queues, cpus, ios, scheduler, clock, final=False):
    """
    Display the state of the system dynamically while it is running and 
    display summarized statistics when all jobs are terminated.
    """
    os.system("cls" if os.name == "nt" else "clear")  # Clear the console

    console = Console()
    console.print(f"[bold magenta]Current Clock Tick: {clock}[/bold magenta]")  # Print the current clock tick

    if not final:  # Runtime visualization
        # Table for Runtime Process Information
        process_table = Table(
            title=f"[bold green]Running Processes ({scheduler.algorithm})[/bold green]",
            show_lines=True,  # Adds lines between rows for better readability
            box=ROUNDED,  # Use ROUNDED from rich.box
        )
        process_table.add_column("Process ID", style="cyan", header_style="bold cyan")
        process_table.add_column("Arrival Time", style="yellow", header_style="bold yellow")
        process_table.add_column("Ready Wait Time", style="magenta", header_style="bold magenta")
        process_table.add_column("I/O Wait Time", style="blue", header_style="bold blue")
        process_table.add_column("Run Time", style="green", header_style="bold green")
        process_table.add_column("CPU", style="white", header_style="bold white")
        process_table.add_column("I/O", style="white", header_style="bold white")
        process_table.add_column("CPU Utilization (%)", style="bright_blue", header_style="bold bright_blue")

        # Add unique jobs to the table
        total_cpu_time = scheduler.total_time
        seen_jobs = set()  # Track unique job IDs

        # Collect jobs from all queues, including MLFQ levels if applicable
        for job in sum(queues.values(), []):  # All non-MLFQ queues
            if job.job_id not in seen_jobs:
                seen_jobs.add(job.job_id)

        if scheduler.algorithm == "MLFQ":
            for level, queue in enumerate(scheduler.mlfq_queues):  # Include MLFQ queues
                for job in queue:
                    if job.job_id not in seen_jobs:
                        seen_jobs.add(job.job_id)

        # Populate the table with unique jobs
        for job_id in seen_jobs:
            job = next((j for j in sum(queues.values(), []) if j.job_id == job_id), None)
            if not job and scheduler.algorithm == "MLFQ":
                for level_queue in scheduler.mlfq_queues:
                    job = next((j for j in level_queue if j.job_id == job_id), None)
                    if job:
                        break
            if job:
                assigned_cpu = next(
                    (f"CPU {cpu['id']}" for cpu in cpus if cpu["job"] and cpu["job"].job_id == job.job_id),
                    "None"
                )
                assigned_io = next(
                    (f"I/O {io['id']}" for io in ios if io["job"] and io["job"].job_id == job.job_id),
                    "None"
                )
                cpu_utilization = (job.run_time / total_cpu_time) * 100 if total_cpu_time > 0 else 0
                process_table.add_row(
                    str(job.job_id),
                    str(job.arrival_time),
                    str(job.ready_wait_time),
                    str(job.io_wait_time),
                    str(job.run_time),
                    assigned_cpu,
                    assigned_io,
                    f"{cpu_utilization:.2f}",
                )

        # Table for Process States
        process_states_table = Table(
            title=f"[bold green]Process States ({scheduler.algorithm})[/bold green]",
            show_lines=True,
            box=ROUNDED,
        )
        process_states_table.add_column("State", style="cyan", header_style="bold cyan")
        process_states_table.add_column("Jobs (Job ID | Priority)", style="yellow", header_style="bold yellow")

        # Add states to the table
        for state_name, state_queue in queues.items():
            if scheduler.algorithm == "MLFQ" and state_name == "Ready":
                for level, queue in enumerate(scheduler.mlfq_queues):  # Iterate through MLFQ queues
                    jobs_with_priorities = ", ".join(
                        f"{job.job_id} (P{job.priority})" if job.priority is not None else str(job.job_id)
                        for job in queue
                    ) if queue else "Empty"
                    process_states_table.add_row(f"MLFQ Level {level}", jobs_with_priorities)
            else:
                jobs_with_priorities = ", ".join(
                    f"{job.job_id} (P{job.priority})" if job.priority is not None else str(job.job_id)
                    for job in state_queue
                ) if state_queue else "Empty"
                process_states_table.add_row(state_name, jobs_with_priorities)

        # Print both tables side by side
        console.print(process_table)
        console.print(process_states_table)

    else:  # Final summary after all jobs are terminated
        # (No changes to the final summary part of the code)
        pass
