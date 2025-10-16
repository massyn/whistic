#!/usr/bin/env python3

from whistic_sdk import Whistic
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Enable logging to see API calls
logging.basicConfig(level=logging.INFO)

# Initialize the client
client = Whistic()

# Test the domain functionality
test_domains = [
    "massyn.net",
    "whistic.com",
    "microsoft.com",
    "google.com",
    "amazon.com",
    "example.com",  # This one probably won't exist
    "nonexistent-domain-12345.com"  # This definitely won't exist
]

print("Testing vendor domain lookup functionality...\n")

for domain in test_domains:
    print(f"Searching for vendor with domain: {domain}")
    print("-" * 50)

    try:
        vendor_data = client.vendors.domain(domain)

        if vendor_data:
            print(f"✓ Found vendor for domain {domain}:")
            print(f"  Raw response: {vendor_data}")
            print()

            # Try to extract useful information based on actual structure
            if isinstance(vendor_data, dict):
                for key, value in vendor_data.items():
                    print(f"  {key}: {value}")
        else:
            print(f"✗ No vendor found for domain: {domain}")

    except Exception as e:
        print(f"✗ Error searching for domain {domain}: {e}")

    print()  # Empty line for readability

print("Domain lookup test completed.")