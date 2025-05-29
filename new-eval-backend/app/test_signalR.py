import asyncio
import websockets

async def connect_to_signalr():
    # Replace with the URL and access token from the /signalr/negotiate response
    base_url = "wss://llm-eval-signalr.service.signalr.net/client/?hub=evaluation"
    access_token = "SharedAccessSignature sr=https%3A%2F%2Fllm-eval-signalr.service.signalr.net&sig=Lwz1MqJcr%2FtGhidn503gD3d6r2kQUgbovQvbKGFXgBM%3D&se=1746640877"

    # Append the access token to the URL as a query parameter
    url = f"{base_url}&access_token={access_token}"

    headers = {
        "Authorization": access_token
    }

    async with websockets.connect(url, extra_headers=headers) as websocket:
        print("Connected to SignalR")
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            print("Received message:", message)

# Run the WebSocket client
asyncio.run(connect_to_signalr())