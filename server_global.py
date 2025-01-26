import subprocess
import sys

def run_ngrok(port):
    """Runs ngrok to tunnel a local port to a global address."""
    try:
        # Use subprocess to execute ngrok command
        result = subprocess.run(
            ["ngrok", "http", str(port)], capture_output=True, text=True, check=True
        )
        # Extract the public URL from the ngrok output
        global_url = result.stdout.strip().split('\n')[0]
        print(f"Your global URL is: {global_url}")
        return global_url
    except FileNotFoundError:
        print("Error: ngrok not found. Please install it.", file=sys.stderr)
        sys.exit(1)  # Exit with an error code
    except subprocess.CalledProcessError as e:
        print(f"Error running ngrok: {e.stderr}", file=sys.stderr)
        sys.exit(1)  # Exit with an error code
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    try:
        port = int(input("Enter the port number (default is 8000): ") or "8000")
    except ValueError:
        print("Invalid port number. Using default 8000.")
        port = 8000

    run_ngrok(port)

if __name__ == "__main__":
    main()