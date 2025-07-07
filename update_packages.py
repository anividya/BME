import subprocess
import json

# Get outdated packages in JSON format
result = subprocess.run(
    ['pip', 'list', '--outdated', '--format=json'],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Error fetching outdated packages:")
    print(result.stderr)
    exit(1)

try:
    outdated_packages = json.loads(result.stdout)
except json.JSONDecodeError:
    print("Failed to parse pip output as JSON.")
    exit(1)

# Update each package
for pkg in outdated_packages:
    pkg_name = pkg['name']
    print(f"Upgrading {pkg_name}...")
    subprocess.run(['pip', 'install', '--upgrade', pkg_name])