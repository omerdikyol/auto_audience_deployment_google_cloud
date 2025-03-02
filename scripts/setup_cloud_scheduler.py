#!/usr/bin/env python3
"""
Script to set up Cloud Scheduler jobs for audience deployment.
This script reads from config/scheduler_config.json and creates Cloud Scheduler jobs.
"""

import json
import os
import argparse
import subprocess
from typing import Dict, List, Any

def load_scheduler_config(config_path: str) -> Dict[str, Any]:
    """Load scheduler configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scheduler config: {str(e)}")
        return {"schedules": []}

def create_scheduler_job(
    job_name: str,
    schedule: str,
    time_zone: str,
    audience_file: str,
    platforms: List[str],
    function_url: str,
    service_account: str,
    project_id: str
) -> bool:
    """Create a Cloud Scheduler job using gcloud command."""
    try:
        # Create the message body as a JSON string
        message_body = json.dumps({
            "gcs_file_path": audience_file,
            "platforms": platforms
        })
        
        # Build the gcloud command
        command = [
            "gcloud", "scheduler", "jobs", "create", "http", job_name,
            "--schedule", schedule,
            "--time-zone", time_zone,
            "--uri", function_url,
            "--message-body", message_body,
            "--headers", "Content-Type=application/json",
            "--oidc-service-account-email", service_account,
            "--project", project_id
        ]
        
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully created scheduler job: {job_name}")
            return True
        else:
            print(f"Failed to create scheduler job {job_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating scheduler job {job_name}: {str(e)}")
        return False

def main():
    """Main function to set up Cloud Scheduler jobs."""
    parser = argparse.ArgumentParser(description='Set up Cloud Scheduler jobs for audience deployment')
    parser.add_argument('--config', default='config/scheduler_config.json', help='Path to scheduler config JSON file')
    parser.add_argument('--function-url', required=True, help='URL of the deployed Cloud Function')
    parser.add_argument('--service-account', required=True, help='Service account email for the scheduler jobs')
    parser.add_argument('--project-id', required=True, help='Google Cloud Project ID')
    
    args = parser.parse_args()
    
    # Load scheduler configuration
    config = load_scheduler_config(args.config)
    
    # Create scheduler jobs
    success_count = 0
    total_jobs = len(config.get("schedules", []))
    
    for job in config.get("schedules", []):
        job_name = job.get("name")
        schedule = job.get("schedule")
        time_zone = job.get("time_zone", "UTC")
        audience_file = job.get("audience_file")
        platforms = job.get("platforms", [])
        
        if not all([job_name, schedule, audience_file, platforms]):
            print(f"Skipping job with missing required fields: {job}")
            continue
        
        success = create_scheduler_job(
            job_name=job_name,
            schedule=schedule,
            time_zone=time_zone,
            audience_file=audience_file,
            platforms=platforms,
            function_url=args.function_url,
            service_account=args.service_account,
            project_id=args.project_id
        )
        
        if success:
            success_count += 1
    
    print(f"Created {success_count} of {total_jobs} scheduler jobs")

if __name__ == "__main__":
    main()
