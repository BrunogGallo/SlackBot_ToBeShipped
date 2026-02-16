import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from datetime import datetime
from clients.mintsoft_get_order import MintsoftOrderClient
import time

load_dotenv()

CLIENT = WebClient(token= os.getenv("SLACK_TOKEN"))
CHANNEL = "C0ADGRZHN7R"

def get_current_date():
    # Obtener fecha actual en formato Mintsoft
    return datetime.now().strftime("%Y-%m-%dT00:00:00")

start = time.time()
duration = 30000 # Para que corra por 8hs
todays_orders = []
no_orders_notice = False

ms_client = MintsoftOrderClient()

while time.time() < start + duration:
    try:
        print("Consultando clients...")
        clients = ms_client.get_clients()

        print("Consultando órdenes...")
        orders = ms_client._get_orders_combined()

        print("Filtrando órdenes...")
        orders_to_be_despatched = ms_client.filter_todays_orders(orders)

        # Si esta vacio, significa que ninguna orden tiene DD para el dia de hoy
        if not orders_to_be_despatched:
            if no_orders_notice == False:
                CLIENT.chat_postMessage(
                    channel = CHANNEL,
                    text = f"De momento, no hay ordenes packeadas para despachar"
                )
                no_orders_notice = True

        #Si tiene algo, es que hay ordenes para despachar
        else:
            for order in orders_to_be_despatched:
                order_id = order.get("ID")
                order_number = order.get("OrderNumber")
                order_client_id = order.get("ClientId")
                items = order.get("TotalItems")

                client_info = next((c for c in clients if c.get("ID") == order_client_id), None)
                client_name = client_info.get("Name")

                #Si hoy no se envio un mensaje al canal para esa orden:
                if order_number not in todays_orders:
                    CLIENT.chat_postMessage(
                        channel = CHANNEL, # <--- CAMBIA ESTO POR EL ID REAL
                        text = f"Numero de Orden: {order_number} - Cliente: {client_name} - Cantidad de Items: {items}"
                    )
                    print("Mensaje enviado con exito")
                    #Almacenar el numero de orden
                    todays_orders.append(order_number)
                    time.sleep(1)

                else:
                    print(f"Mensaje ya enviado para la orden {order_number}")

    except SlackApiError as e:
        print(f"Error de Slack API: {e.response['error']}")

    except Exception as e:
        print(f"Error inesperado: {e}")
        print(clients.status_code)
        print(clients.text[:500])

    time.sleep(1800) #Revisa las ordenes cada 30min
