# Whistic SDK

A Python SDK to interface with the Whistic API for vendor management and third-party risk management operations.

## Installation

### From PyPI (Recommended)

```bash
pip install whistic
```

### From Source

```bash
git clone https://github.com/massyn/whistic.git
cd whistic
pip install -e .
```

## Requirements

* Python 3.7 or higher
* Create an [API Key](https://whistichelp.zendesk.com/hc/en-us/articles/14823790530071-API-Key-Creation) on the Whistic platform

## Quick Start

### Environment Setup

Create a `.env` file in your project root or set the environment variable:

```bash
export WHISTIC_TOKEN=your_api_token_here
```

Or create a `.env` file:
```
WHISTIC_TOKEN=your_api_token_here
```

### Basic Usage

```python
from whistic_sdk import Whistic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = Whistic()

# List all vendors
vendors = client.vendors.list()
print(f"Found {len(vendors)} vendors")

# Get detailed information for all vendors (parallel processing)
detailed_vendors = client.vendors.describe()

# Get a specific vendor
vendor_id = vendors[0]['identifier']
vendor_details = client.vendors.get(vendor_id)

# Update a vendor
client.vendors.update(vendor_id, {
    "name": "Updated Vendor Name",
    "description": "Updated description"
})

# Create a new vendor
new_vendor_data = {
    "name": "New Vendor",
    "description": "A new vendor",
    # ... other vendor fields
}
client.vendors.new(new_vendor_data)
```

## Advanced Usage

### Custom Configuration

```python
from whistic_sdk import Whistic

# Configure with custom settings
client = Whistic(max_workers=10)  # Increase parallel processing workers
```

### Batch Operations

```python
# Process all vendors in parallel
all_vendors = client.vendors.describe()

# Filter and update multiple vendors
for vendor in all_vendors:
    if vendor.get('status') == 'pending':
        client.vendors.update(vendor['identifier'], {
            'status': 'active'
        })
```

### Error Handling

```python
import logging

# Enable debug logging to see API calls
logging.basicConfig(level=logging.DEBUG)

try:
    vendor = client.vendors.get('non-existent-id')
except Exception as e:
    print(f"Error fetching vendor: {e}")
```

## API Reference

### Whistic Class

The main client class for interacting with the Whistic API.

#### Constructor
- `Whistic(max_workers=5)`: Initialize client with optional max workers for parallel processing

#### Properties
- `vendors`: Access to vendor management operations

### Vendors Class

Handles all vendor-related operations.

#### Methods

- **`list()`**: Get paginated list of all vendor identifiers
  - Returns: List of vendor objects with basic information

- **`describe()`**: Get detailed information for all vendors using parallel processing
  - Returns: List of complete vendor objects with all details

- **`get(vendor_id)`**: Fetch detailed information for a specific vendor
  - Parameters: `vendor_id` (str) - The vendor identifier
  - Returns: Complete vendor object or None if not found

- **`update(vendor_id, data)`**: Update vendor information
  - Parameters: 
    - `vendor_id` (str) - The vendor identifier
    - `data` (dict) - Dictionary with fields to update
  - Note: Uses deep merge to preserve existing data

- **`new(data)`**: Create a new vendor
  - Parameters: `data` (dict) - Complete vendor data structure

## Features

- **Automatic Pagination**: Handles API pagination automatically
- **Parallel Processing**: Concurrent API calls for better performance
- **Rate Limiting**: Built-in retry logic with exponential backoff
- **Deep Merge Updates**: Safely update vendor data without losing existing fields
- **Colored Logging**: Enhanced console output for debugging
- **Environment Variable Support**: Secure token management

## Error Handling

The SDK includes comprehensive error handling:

- **Rate Limiting**: Automatic retry with exponential backoff for 429 responses
- **Request Timeouts**: 30-second timeout on all API calls
- **Connection Errors**: Graceful handling of network issues
- **API Errors**: Detailed error logging with response codes and messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Reference

* [Whistic API Documentation](https://public.whistic.com/swagger-ui/index.html)
* [API Key Creation Guide](https://whistichelp.zendesk.com/hc/en-us/articles/14823790530071-API-Key-Creation)
