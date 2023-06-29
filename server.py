import asyncio
import json
import time

transports = []
time_data = {"time": 0, "unix_time": 0, "is_playing": True}

class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        print("hg")
        self.transport = transport
        self.username = ""
        transports.append(transport)

        self.send_data_to_all_except_me({"action": "connect", "online_count": len(transports), "is_me": False})
        self.send_data({"action": "connect", "online_count": len(transports), "is_me": True})
        if time_data["unix_time"] == 0:
            time_data["unix_time"] = time.time()
        self.send_time(False)

    def connection_lost(self, exc):
        self.send_data_to_all_except_me({"action": "disconnect", "username": self.username, "online_count": len(transports)-1})
        transports.remove(self.transport)
        
    def data_received(self, received_data):
        data = json.loads(received_data.decode("utf-8"))
        print(data)

        if data["action"] == "message":
            self.username = data["username"]
            self.send_data_to_all({"action": "message", "username": data["username"], "message": data["message"], "is_time_message": data["is_time_message"]})
        elif data["action"] == "time":
            time_data["time"] = data["time"]
            time_data["unix_time"] = time.time()
            time_data["is_playing"] = data["is_playing"]
            self.send_time()

    def send_time(self, to_all=True):
        if to_all:
            self.send_data_to_all_except_me({"action": "time", "time": time_data["time"], "unix_time": time_data["unix_time"], "is_playing": time_data["is_playing"]})
        else:
            self.send_data({"action": "time", "time": time_data["time"], "unix_time": time_data["unix_time"], "is_playing": time_data["is_playing"]})

    def send_data(self, data):
        self.transport.write(json.dumps(data).encode("utf-8"))

    def send_data_to_all(self, data):
        for transport in transports:
            transport.write(json.dumps(data).encode("utf-8"))

    def send_data_to_all_except_me(self, data):
        for transport in transports:
            if transport != self.transport:
                transport.write(json.dumps(data).encode("utf-8"))

async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '0.0.0.0', 8888)

    async with server:
        await server.serve_forever()


asyncio.run(main())
