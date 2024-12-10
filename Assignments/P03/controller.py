import os

PIPE_PATH = "/tmp/simulation_control"

def send_command(command):
    if os.path.exists(PIPE_PATH):
        with open(PIPE_PATH, "w") as pipe:
            pipe.write(command)
    else:
        print("Error: Named pipe not available.")

def main():
    print("Controller started. Use 'p' to pause, 'r' to resume.")
    while True:
        command = input("Enter command (p/r): ").strip().lower()
        if command in ["p", "r"]:
            send_command(command)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
