import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


class Vendors:
    def __init__(self, whistic_instance):
        self.whistic = whistic_instance

    def list(self):
        logging.debug("Querying vendors")
        url = f"{self.whistic.endpoint}/vendors?page_size={self.whistic.page_size}"

        all_vendor_identifiers = []
        
        while True:
            response = self.whistic._make_request_with_retry(url)
            
            if response and response.status_code == 200:
                logging.info(f"{response.status_code} - {url}")
                response_data = response.json()
                
                for v in response_data['_embedded']['vendors']:
                    all_vendor_identifiers.append(v)

                if 'next' in response_data['_links']:
                    next_url = response_data['_links']['next']['href']
                    if next_url == url:
                        break
                    else:
                        url = next_url
                else:
                    break
            else:
                break

        logging.info(f"Found {len(all_vendor_identifiers)} vendors. Fetching details in parallel...")
        return all_vendor_identifiers
    
    def describe(self):
        all_vendor_identifiers = []
        for v in self.list():
            all_vendor_identifiers.append(v['identifier'])
        data = []
        with ThreadPoolExecutor(max_workers=self.whistic.max_workers) as executor:
            future_to_identifier = {executor.submit(self.get, identifier): identifier 
                                  for identifier in all_vendor_identifiers}
            
            for future in as_completed(future_to_identifier):
                identifier = future_to_identifier[future]
                try:
                    vendor_data = future.result()
                    if vendor_data:
                        data.append(vendor_data)
                except Exception as e:
                    logging.error(f"Failed to fetch vendor {identifier}: {e}")

        logging.info(f"Successfully retrieved {len(data)} vendors")
        return data

    def get(self, vendor_id):
        """Fetch individual vendor details"""
        url = f"{self.whistic.endpoint}/vendors/{vendor_id}"
        response = self.whistic._make_request_with_retry(url)
        
        if response and response.status_code == 200:
            logging.info(f"{response.status_code} - {url}")
            return response.json()
        else:
            if response:
                logging.error(f"{response.status_code} - {url} - {response.content}")
            return None

    def _deep_merge(self, orig, update_data):
        """Recursively merge update_data into orig, only updating existing keys"""
        for key, value in update_data.items():
            if key not in orig:
                logging.warning(f"Key '{key}' not found in original data, skipping")
                continue
                
            if isinstance(value, dict) and isinstance(orig[key], dict):
                # Recursively merge nested dictionaries
                self._deep_merge(orig[key], value)
            else:
                # Update the value directly
                orig[key] = value

    def update(self, vendor_id, data):
        url = f"{self.whistic.endpoint}/vendors/{vendor_id}?ignore_missing_custom_fields=true"
        orig = self.get(vendor_id)
        
        # Deep merge the data into orig
        self._deep_merge(orig, data)

        response = requests.put(url, json=orig, headers=self.whistic.headers, timeout=30)
        if response.status_code == 200:
            logging.info(f"{response.status_code} - {url}")
        else:
            logging.error(f"{response.status_code} - {url} - {response.content}")

    def new(self, data):
        import json
        print(json.dumps(data,indent=2))

        print(self.whistic.headers)

        url = f"{self.whistic.endpoint}/vendors?ignore_missing_custom_fields=true"
        response = requests.post(url, json=data, headers=self.whistic.headers, timeout=30)
        if response.status_code in [200, 201]:
            logging.info(f"{response.status_code} - {url}")
            return True
        else:
            logging.error(f"{response.status_code} - {url} - {response.content}")
            return False

    def domain(self, domain):
        """Retrieve vendor details by domain name"""
        url = f"{self.whistic.endpoint}/vendorDomains/{domain}"
        response = self.whistic._make_request_with_retry(url)

        if response and response.status_code == 200:
            logging.info(f"{response.status_code} - {url}")
            data = response.json()
            # API may return a list, so handle both cases
            if isinstance(data, list):
                return data[0] if data else None
            return data
        else:
            if response:
                logging.error(f"{response.status_code} - {url} - {response.content}")
            return None