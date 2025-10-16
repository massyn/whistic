#!/usr/bin/env python3
"""
Vendor Intake Form Submission Dictionary

This example shows the proper structure for submitting a vendor intake form
using the Whistic SDK. Use this as a template for building your submissions.
"""

from whistic_sdk import Whistic
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    client = Whistic()

    # Submit the form
    client.vendor_intake_form.vendor_intake({
        "Vendor Information:Information Asset ID"                           : "12345",
        "Vendor Information:Job Title"                                      : "CISO",           # mandatory field
        "Vendor Information:Vendor URL"                                     : "example38.com",
        "Vendor Information:Vendor Name"                                    : "Example Corp HLRA ID",
        "Vendor Information:Product / Service Name"                         : "Cloud Patform",
        "Vendor Information:Write a description of the vendor / service"    : "Cloud Platform",
        "Vendor Information:First Name"                                     : "Bob",
        "Vendor Information:Last Name"                                      : "Tester",
        "Vendor Information:Email Address"                                  : "bob@example.com",
        "Vendor Information:Type of Vendor"                                 : "Current: we already work with this vendor",
        "Primary Business Owner Information:First Name"                     : "Joe",
        "Primary Business Owner Information:Last Name"                      : "Blobs",
        "Primary Business Owner Information:Email Address"                  : "joe@blobs.com",
        "CIA Rating and Asset Tiering:Confidentiality"                      : "Minor",
        "HLRA Questionnaire :What data or information will be shared?"      : "Only PII"
    })

