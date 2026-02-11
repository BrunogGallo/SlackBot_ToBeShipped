import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_current_date():
    #Almacenar fecha actual
    now = datetime.now()

    #Transformar al formato de Mintsoft
    yyyymmdd = datetime.date(now)
    current_despatch_date = f"{yyyymmdd}T00:00:00"

    return current_despatch_date

class MintsoftOrderClient:
    
    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self):
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.client_id = os.getenv("MINTSOFT_CLIENT_ID")
        self.channel_id = os.getenv("CHANNEL_ID")

        if not all([self.username, self.password, self.client_id]):
            raise RuntimeError(
                "Missing Mintsoft credentials "
                "(MINTSOFT_USERNAME / MINTSOFT_PASSWORD / MINTSOFT_CLIENT_ID)"
            )

        self.api_key = self._authenticate()
        

    def _authenticate(self) -> str:
        url = f"{self.BASE_URL}/api/Auth"

        payload = {
            "Username": self.username,
            "Password": self.password,
        }

        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()

        return r.json()
    

    def headers(self) -> Dict[str, str]:
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    
    def _get_orders_combined(self) -> List[Dict[str, Any]]:

        status_ids = [17, 20] #Picked y Packed
        all_orders = []

        for status_id in status_ids:
            params = {
                "Limit": 100,
                "OrderStatusId": status_id,
            }
            r = requests.get(
                f"{self.BASE_URL}/api/Order/List",
                headers=self.headers(),
                params=params,
                timeout=30,
            )
            if r.status_code == 200:
                all_orders.extend(r.json())
    
        return all_orders
    
    
    def filter_todays_orders(self, orders):
        today = get_current_date()
        orders_to_be_despatched = []

        for order in orders:
            despatch_date = order.get("RequiredDespatchDate")

            if despatch_date == today: 
                orders_to_be_despatched.append(order)
            
        return orders_to_be_despatched