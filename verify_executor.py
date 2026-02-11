import httpx
import asyncio
import json

async def call():
    url = "http://127.0.0.1:8000/api/v1/call"
    payload = {
        "domain": "core.execute", 
        "params": {
            "func_name": "sleep", 
            "params": {"seconds": 2}
        },
        "context": {
            "caller_id": "tester",
            "trace_stack": []
        }
    }
    
    print(f"Sending request to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=5.0)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(call())
