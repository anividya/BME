# run_celery.py
import subprocess
import sys
import os

project_name = "BME"  # 🔁 Change to your project name

try:
    # Run Celery Worker
    worker = subprocess.Popen(
        ["celery", "-A", project_name, "worker", "--loglevel=info"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Run Celery Beat
    beat = subprocess.Popen(
        ["celery", "-A", project_name, "beat", "--loglevel=info"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    print("Celery worker and beat started. Press Ctrl+C to stop.")

    # Wait for both processes to finish
    worker.wait()
    beat.wait()

except KeyboardInterrupt:
    print("Stopping processes...")
    worker.terminate()
    beat.terminate()
