import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import logging  # For logging output to a file

# Configure logging to output to a file
logging.basicConfig(
    filename="simulation_output.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(message)s"  # Log format
)

def visualize_all(queues, cpus, ios, scheduler, clock):
    """
    Display the state of the system dynamically, combining Process Statistics, Performance Metrics, and States in tables.
    Includes the scheduler algorithm as a title in all tables.
    For MLFQ, display MLFQ queues instead of the Ready queue.
    """
    os.system("cls" if os.name == "nt" else "clear")  # Clear the console

    console = Console()
    console.print(f"[bold magenta]Current Clock Tick: {clock}[/bold magenta]")
    logging.info(f"Current Clock Tick: {clock}")  # Log clock tick

    # Unified Table: Process Statistics and Performance Metrics
    process_table = Table(
        title=f"[bold green]Processes & Performance Metrics ({scheduler.algorithm})[/bold green]",
        show_edge=False,
        box=None,
    )
    process_table.add_column("Process ID", style="cyan")
    process_table.add_column("Arrival Time", style="yellow")
    process_table.add_column("Ready Time", style="magenta")
    process_table.add_column("Running Time", style="green")
    process_table.add_column("Waiting Time", style="blue")
    process_table.add_column("IO Time", style="purple")
    process_table.add_column("Turnaround Time", style="bright_yellow")
    process_table.add_column("Exit Time", style="red")

    # Populate Process Data
    for job in queues["Terminated"]:
        process_table.add_row(
            str(job.job_id),
            str(job.arrival_time),
            str(job.ready_wait_time),
            str(job.run_time),
            str(job.ready_wait_time),
            str(job.io_wait_time),
            str(job.turnaround_time if job.terminated else "N/A"),
            str(job.terminated_time if job.terminated else "N/A"),
        )

    # Calculate Metrics
    total_jobs = len(queues["Terminated"])
    avg_arrival_time = (
        sum(job.arrival_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    avg_ready_time = (
        sum(job.ready_wait_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    avg_running_time = (
        sum(job.run_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    avg_waiting_time = (
        sum(job.ready_wait_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    avg_io_time = (
        sum(job.io_wait_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    avg_tat = (
        sum(job.turnaround_time for job in queues["Terminated"]) / total_jobs if total_jobs > 0 else 0
    )
    cpu_utilization = (scheduler.cpu_busy_time / scheduler.total_time) * 100 if scheduler.total_time > 0 else 0

    # Add Averages Row
    process_table.add_row(
        "Averages:",
        f"{avg_arrival_time:.4f}",
        f"{avg_ready_time:.4f}",
        f"{avg_running_time:.4f}",
        f"{avg_waiting_time:.4f}",
        f"{avg_io_time:.4f}",
        f"{avg_tat:.4f}",
        "N/A",
    )

    # Add CPU Utilization Row
    process_table.add_row(
        "CPU Utilization:",
        "",
        "",
        "",
        "",
        "",
        "",
        f"{cpu_utilization:.2f}%",
    )

    console.print(process_table)

    # Table for CPU and I/O States
    state_table = Table(
        title=f"[bold green]CPU & I/O States ({scheduler.algorithm})[/bold green]",
        show_edge=False,
        box=None,
    )
    state_table.add_column("Type", style="cyan")
    state_table.add_column("ID", style="yellow")
    state_table.add_column("Job ID", style="magenta")
    state_table.add_column("Remaining Time", style="green")

    for cpu in cpus:
        job_id = str(cpu["job"].job_id) if cpu["job"] else "Idle"
        remaining_time = str(cpu["remaining_time"]) if cpu["job"] else "-"
        state_table.add_row("CPU", str(cpu["id"]), job_id, remaining_time)

    for io in ios:
        job_id = str(io["job"].job_id) if io["job"] else "Idle"
        remaining_time = str(io["remaining_time"]) if io["job"] else "-"
        state_table.add_row("I/O", str(io["id"]), job_id, remaining_time)

    console.print(state_table)

    # Conditionally display MLFQ Queues
    if scheduler.algorithm == "MLFQ":
        mlfq_table = Table(
            title=f"[bold green]MLFQ Queues ({scheduler.algorithm})[/bold green]",
            show_edge=False,
            box=None,
        )
        mlfq_table.add_column("Queue Level", style="cyan")
        mlfq_table.add_column("Jobs (Job ID | Priority)", style="yellow")

        for level, queue in enumerate(scheduler.mlfq_queues):
            jobs_with_priorities = ", ".join(
                f"{job.job_id} (P{job.priority})" if job.priority is not None else str(job.job_id)
                for job in queue
            ) if queue else "Empty"
            mlfq_table.add_row(f"Level {level}", jobs_with_priorities)

        console.print(mlfq_table)

    # Table for Process States
    process_states_table = Table(
        title=f"[bold green]Process States ({scheduler.algorithm})[/bold green]",
        show_edge=False,
        box=None,
    )
    process_states_table.add_column("State", style="cyan")
    process_states_table.add_column("Jobs (Job ID | Priority)", style="yellow")

    for state_name, state_queue in queues.items():
        if scheduler.algorithm != "MLFQ" or state_name != "Ready":  # Exclude Ready for MLFQ
            jobs_with_priorities = ", ".join(
                f"{job.job_id} (P{job.priority})" if job.priority is not None else str(job.job_id)
                for job in state_queue
            ) if state_queue else "Empty"
            process_states_table.add_row(state_name, jobs_with_priorities)

    console.print(process_states_table)


