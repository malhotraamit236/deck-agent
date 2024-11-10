import httpx
from typing import Type, TypeVar, Generic
from dataclasses import dataclass
from config import load_config

T = TypeVar('T')

class ApiClient(Generic[T]):
    def __init__(self):
        config = load_config()
        self.base_url = config['base_url']
        self.timeout = config['timeout']
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get(self, endpoint: str, model: Type[T]) -> T:
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()  

            data = response.json()
            
            if isinstance(data, dict):
                return model(**data)  
            
            if isinstance(data, list):
                return [model(**item) for item in data]

            raise ValueError(f"Unexpected response data format: {data}")

        except httpx.RequestError as e:
            print(f"An error occurred while requesting {endpoint}: {e}")
            raise
        except ValueError as e:
            print(f"Failed to parse response for {endpoint}: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
