import requests

class JobManager:
    """
    Manages interaction with the job API and fetches job/burst details.
    """
    BASE_URL = "http://profgriffin.com:8000"

    def __init__(self, config):
        self.config = config
        
    def init_simulation(self, seed=None):
        """
        Initialize simulation with the server.
        Optionally pass a seed value for reproducibility.
        """
        # Add seed to the route if provided
        route = f"{self.BASE_URL}/init"
        if seed is not None:
            route += f"?seed={seed}"

        # Send the request
        response = requests.post(route, json=self.config)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()

        return data["start_clock"], data["session_id"], data["time_slice"]

    def get_new_jobs(self, session_id, clock_time):
        """
        Fetch new jobs for the given clock time.
        """
        response = requests.get(f"{self.BASE_URL}/job", params={
            "client_id": self.config["client_id"],
            "session_id": session_id,
            "clock_time": clock_time
        })
        response.raise_for_status()
        return response.json().get("data", [])

    def fetch_bursts(self, session_id, job_id):
        """
        Fetch burst details for a specific job.
        """
        response = requests.get(f"{self.BASE_URL}/burst", params={
            "client_id": self.config["client_id"],
            "session_id": session_id,
            "job_id": job_id
        })
        if response.status_code == 200 and response.json().get("success"):
            bursts = response.json()["data"]
            # Ensure bursts are returned as a list
            if isinstance(bursts, dict):  # If single burst is returned as a dict
                return [bursts]
            return bursts
        return []


    def jobs_left(self, session_id):
        """
        Check if any jobs are left in the system.
        """
        response = requests.get(f"{self.BASE_URL}/jobsLeft", params={
            "client_id": self.config["client_id"],
            "session_id": session_id
        })
        response.raise_for_status()
        return int(response.text) > 0
