#!/usr/bin/env python3
"""
Basic usage example for the Whistic SDK

This script demonstrates how to use the Whistic SDK to interact with the Whistic API.
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
    
    # List all vendors
    print("Fetching vendor list...")
    vendors = client.vendors.list()
    print(f"Found {len(vendors)} vendors")
    
    # Save vendor list to file
    with open('vendors_list.json', 'w') as f:
        json.dump(vendors, f, indent=2)
    print("Vendor list saved to vendors_list.json")
    
    if vendors:
        # Get detailed information for the first vendor
        vendor_id = vendors[0]['identifier']
        print(f"Fetching details for vendor: {vendor_id}")
        
        vendor_details = client.vendors.get(vendor_id)
        if vendor_details:
            print(f"Vendor name: {vendor_details.get('name', 'N/A')}")
            print(f"Vendor status: {vendor_details.get('status', 'N/A')}")
            
            # Save detailed vendor info
            with open(f'vendor_{vendor_id}_details.json', 'w') as f:
                json.dump(vendor_details, f, indent=2)
            print(f"Vendor details saved to vendor_{vendor_id}_details.json")
    
    # Uncomment the following lines to test vendor creation and updates
    # WARNING: This will create/modify actual vendor data
    
    # # Example: Update a vendor (uncomment to test)
    # if vendors:
    #     vendor_id = vendors[0]['identifier']
    #     print(f"Updating vendor: {vendor_id}")
    #     client.vendors.update(vendor_id, {
    #         "description": "Updated via Whistic SDK example"
    #     })
    #     print("Vendor updated successfully")
    
    # # Example: Create a new vendor (uncomment to test)
    # new_vendor_data = {
    #     "name": "Example Vendor",
    #     "description": "Created via Whistic SDK example",
    #     # Add other required fields as needed
    # }
    # print("Creating new vendor...")
    # client.vendors.new(new_vendor_data)
    # print("New vendor created successfully")

    # List all vendors
    print("Fetching vendor list...")
    vendors = client.vendors.describe()
    print(f"Found {len(vendors)} vendors")
    
    # Save vendor list to file
    with open('vendors_describe.json', 'w') as f:
        json.dump(vendors, f, indent=2)
    print("Vendor list saved to vendors_describe.json")
    
    
    print("Example completed successfully!")


if __name__ == "__main__":
    main()