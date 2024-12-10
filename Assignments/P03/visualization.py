import os
from rich.console import Console
from rich.table import Table
import logging  # For logging output to a file

# Configure logging to output to a file
logging.basicConfig(
    filename="simulation_output.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(message)s"  # Log format
)

from rich.box import ROUNDED

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

        # Add running process information
        total_cpu_time = scheduler.total_time
        seen_jobs = set()  # Track unique job IDs

        # Collect jobs assigned to CPU or I/O
        for cpu in cpus:
            if cpu["job"]:
                job = cpu["job"]
                if job.job_id not in seen_jobs:
                    seen_jobs.add(job.job_id)
                    cpu_utilization = (job.run_time / total_cpu_time) * 100 if total_cpu_time > 0 else 0
                    process_table.add_row(
                        str(job.job_id),
                        str(job.arrival_time),
                        str(job.ready_wait_time),
                        str(job.io_wait_time),
                        str(job.run_time),
                        f"CPU {cpu['id']}",
                        "None",
                        f"{cpu_utilization:.2f}",
                    )

        for io in ios:
            if io["job"]:
                job = io["job"]
                if job.job_id not in seen_jobs:
                    seen_jobs.add(job.job_id)
                    cpu_utilization = (job.run_time / total_cpu_time) * 100 if total_cpu_time > 0 else 0
                    process_table.add_row(
                        str(job.job_id),
                        str(job.arrival_time),
                        str(job.ready_wait_time),
                        str(job.io_wait_time),
                        str(job.run_time),
                        "None",
                        f"I/O {io['id']}",
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
        # Table for Completed Jobs
        summary_table = Table(
            title=f"[bold green]Completed Jobs Summary ({scheduler.algorithm})[/bold green]",
            show_lines=True,
            box=ROUNDED,
        )
        summary_table.add_column("Process ID", style="cyan", header_style="bold cyan")
        summary_table.add_column("Arrival Time", style="yellow", header_style="bold yellow")
        summary_table.add_column("Terminated Time", style="red", header_style="bold red")
        summary_table.add_column("Turnaround Time", style="bright_yellow", header_style="bold bright_yellow")
        summary_table.add_column("Ready Wait Time", style="magenta", header_style="bold magenta")
        summary_table.add_column("I/O Wait Time", style="blue", header_style="bold blue")
        summary_table.add_column("CPU Utilization (%)", style="bright_blue", header_style="bold bright_blue")

        # Add terminated job information
        total_tat = 0
        total_ready_wait = 0
        total_io_wait = 0
        total_jobs = len(queues["Terminated"])
        total_cpu_time = scheduler.total_time

        for job in queues["Terminated"]:
            tat = job.turnaround_time or (job.terminated_time - job.arrival_time)
            total_tat += tat
            total_ready_wait += job.ready_wait_time
            total_io_wait += job.io_wait_time
            cpu_utilization = (job.run_time / total_cpu_time) * 100 if total_cpu_time > 0 else 0
            summary_table.add_row(
                str(job.job_id),
                str(job.arrival_time),
                str(job.terminated_time),
                str(tat),
                str(job.ready_wait_time),
                str(job.io_wait_time),
                f"{cpu_utilization:.2f}",
            )

        # Display averages
        avg_tat = total_tat / total_jobs if total_jobs > 0 else 0
        avg_ready_wait = total_ready_wait / total_jobs if total_jobs > 0 else 0
        avg_io_wait = total_io_wait / total_jobs if total_jobs > 0 else 0
        cpu_utilization = (scheduler.cpu_busy_time / scheduler.total_time) * 100 if scheduler.total_time > 0 else 0

        console.print(summary_table)

        # Print overall averages and CPU utilization
        console.print(f"[bold green]Final Statistics:[/bold green]")
        console.print(f"Average Turnaround Time (TAT): [bright_yellow]{avg_tat:.2f}[/bright_yellow]")
        console.print(f"Average Ready Wait Time: [magenta]{avg_ready_wait:.2f}[/magenta]")
        console.print(f"Average I/O Wait Time: [blue]{avg_io_wait:.2f}[/blue]")
        console.print(f"CPU Utilization: [bright_blue]{cpu_utilization:.2f}%[/bright_blue]")


