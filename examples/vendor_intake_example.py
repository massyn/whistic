#!/usr/bin/env python3
"""
Vendor Intake Form Submission Dictionary

This example shows the proper structure for submitting a vendor intake form
using the Whistic SDK. Use this as a template for building your submissions.
"""

from whistic_sdk import Whistic
from dotenv import load_dotenv
# Complete vendor intake form submission dictionary
# Structure: {section_name: {field_name: value}}
vendor_intake_submission = {
    "Vendor Information": {
        # Required fields
        "Vendor URL": "example-vendor.com",
        "Vendor Name": "Example Vendor Inc.",
        "Product / Service Name": "Cloud Security Platform",
        "Write a description of the vendor / service": "Comprehensive cloud security solution",
        "Type of Vendor": "Software Provider",
        "First Name": "John",              # Vendor contact
        "Last Name": "Smith",
        "Email Address": "john.smith@example-vendor.com",

        # Optional fields
        "Information Asset ID": "ASSET-12345",
        "Primary Hosting Region": "US East",
        "Job Title": "Security Manager",
        "Phone Number": "+1-555-123-4567"
    },

    "Primary Business Owner Information": {
        # Required fields
        "First Name": "Jane",               # Internal business owner
        "Last Name": "Doe",
        "Email Address": "jane.doe@company.com",

        # Optional fields
        "Business Unit": "IT Security",
        "Divisions": "Infrastructure, Compliance",
        "Stakeholders Involved": "CISO, IT Manager"
    },

    "CIA Rating and Asset Tiering": {
        # All fields optional
        "Confidentiality": "High",
        "Integrity": "High",
        "Availability": "Medium",
        "Asset Tier": "Tier 1",
        "Information Classification": "Critical"
    }
}

if __name__ == "__main__":
    load_dotenv()
    client = Whistic()

    # Submit the form
    success = client.vendor_intake_form.new(vendor_intake_submission)
    print(f"Submission result: {success}")
