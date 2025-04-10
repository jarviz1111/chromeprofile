"""
API Verification Module
----------------------
Handles API verification and authentication.
"""
import os
import requests

class APIManager:
    """Handles API verification and authentication for the application."""
    
    def __init__(self, api_base_url="https://inboxinnovations.org"):
        """Initialize the API manager.
        
        Args:
            api_base_url (str): Base URL for API requests.
        """
        self.api_base_url = api_base_url
    
    def verify_credentials(self, user_id, key_id):
        """Verify API credentials against the verification endpoint.
        
        Args:
            user_id (str): API user ID.
            key_id (str): API key ID.
            
        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        if not user_id or not key_id:
            return False
            
        try:
            api_link = f"{self.api_base_url}?menuname=seeding&userid={user_id}&keyid={key_id}"
            response = requests.get(api_link, timeout=10)
            return response.text.strip() == "1"
        except requests.RequestException as e:
            print(f"❌ API verification failed: {e}")
            return False
