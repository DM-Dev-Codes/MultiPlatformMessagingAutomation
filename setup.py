import os
import platform
import subprocess
from setuptools import setup, find_packages

# Function to execute a bash script and ensure it's executable on macOS/Linux
def run_bash_script(script_name):
    subprocess.check_call(['chmod', '+x', script_name])
    subprocess.check_call(['./' + script_name])

# Function to execute the PowerShell script on Windows
def run_powershell_script(script_name):
    subprocess.check_call(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_name])

# Detect the operating system
os_type = platform.system()

# Run the appropriate setup script based on the OS
if os_type == "Windows":
    # Run the PowerShell script for Windows
    print("Detected Windows OS. Running setup_database_win.ps1.")
    run_powershell_script('setup_database_win.ps1')
elif os_type == "Darwin" or os_type == "Linux":
    # Run the Bash script for macOS/Linux
    print("Detected macOS/Linux OS. Running setup_database.sh.")
    run_bash_script('setup_database.sh')
else:
    raise Exception(f"Unsupported OS: {os_type}")

setup(
    name="israel_real_time_",  
    version="1.0.0", 
    author="David Marks",  
    author_email="dovidyl@gmail.com",  
    description="A project for managing actions, APIs, and website integrations with Selenium and MySQL",
    long_description=open("README.MD").read(),  
    long_description_content_type="text/markdown", 
    url="https://github.com/davidmarks/jira_project",  
    packages=find_packages(exclude=["tests", "venv"]),  
    include_package_data=True,  
    install_requires=[
        "selenium", 
        "mysql-connector-python",  
        "flask",  
        "schedule", 
        "fastapi",  
       
    ],
    python_requires=">=3.12",  
    entry_points={
        "console_scripts": [
            "jira-website=website.app:main",  
            "jira-actions=action_manager.manage_actions:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
)
