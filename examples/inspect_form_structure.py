#!/usr/bin/env python3

from whistic import Whistic
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Enable logging to see API calls
logging.basicConfig(level=logging.INFO)

# Initialize the client
client = Whistic()

client.vendor_intake_form.show()
