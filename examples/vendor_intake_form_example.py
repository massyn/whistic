#!/usr/bin/env python3
"""
Vendor Intake Form example for the Whistic SDK

This script demonstrates how to retrieve the vendor intake form from the Whistic API.
The vendor intake form contains the structure and questions that vendors need to
complete when onboarding to your organization.

Make sure you have your WHISTIC_TOKEN environment variable set before running.
"""

import json
import os
from dotenv import load_dotenv
from whistic_sdk import Whistic


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Check if token is available
    if not os.getenv('WHISTIC_TOKEN'):
        print("Error: WHISTIC_TOKEN environment variable not set")
        print("Please set your Whistic API token in a .env file or environment variable")
        return

    # Initialize the Whistic client
    print("Initializing Whistic client...")
    client = Whistic()

    # Get the vendor intake form
    print("Fetching vendor intake form...")
    intake_form = client.vendor_intake_form.describe()

    print(json.dumps(intake_form,indent=2))
    
    print("Example completed!")


if __name__ == "__main__":
    main()