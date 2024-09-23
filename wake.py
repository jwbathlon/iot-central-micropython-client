import machine
import utime

# Define your wake-up interval in milliseconds (e.g., 10 minutes)
wake_up_interval_ms = 10 * 60 * 1000

# Your task function
def perform_tasks():
    # Perform your tasks here
    print("Performing tasks...")

# Main program logic
def main():
    while True:
        perform_tasks()
        # Go to light sleep
        print("Going to light sleep.")
        utime.sleep_ms(wake_up_interval_ms)

# Run the main function
if __name__ == "__main__":
    main()