import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://localhost:8000/mcp/"


async def main():
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("Tools discovered:", [t.name for t in tools.tools])
            for item, qty in [("phone", 1), ("laptop", 1), ("headphones", 2)]:
                res = await s.call_tool("process_checkout", {"item": item, "quantity": qty})
                print(item, "->", res.content[0].text)
                await asyncio.sleep(2)

asyncio.run(main())