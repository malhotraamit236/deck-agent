import pytest
from unittest import mock
import httpx
from .api_client import ApiClient
from dataclasses import dataclass
from typing import List

@dataclass
class MyModel:
    id: int
    name: str


@pytest.fixture
def mock_load_config():
    with mock.patch('config.load_config', return_value={'base_url': 'http://test.com', 'timeout': 10}):
        yield


@pytest.mark.asyncio
async def test_get_single_object(mock_load_config):

    with mock.patch('httpx.AsyncClient.get') as mock_get:
    
        mock_get.return_value = mock.MagicMock()
        mock_get.return_value.json.return_value = {'id': 1, 'name': 'Test'}
        mock_get.return_value.raise_for_status = mock.MagicMock()

        async with ApiClient[MyModel]() as client:
            result = await client.get('/test', MyModel)

    
        assert isinstance(result, MyModel)
        assert result.id == 1
        assert result.name == 'Test'


@pytest.mark.asyncio
async def test_get_multiple_objects(mock_load_config):

    with mock.patch('httpx.AsyncClient.get') as mock_get:
    
        mock_get.return_value = mock.MagicMock()
        mock_get.return_value.json.return_value = [{'id': 1, 'name': 'Test 1'}, {'id': 2, 'name': 'Test 2'}]
        mock_get.return_value.raise_for_status = mock.MagicMock()

        async with ApiClient[MyModel]() as client:
            result = await client.get('/test', MyModel)

    
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, MyModel) for item in result)
        assert result[0].name == 'Test 1'
        assert result[1].name == 'Test 2'


@pytest.mark.asyncio
async def test_get_http_error(mock_load_config):

    with mock.patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        async with ApiClient[MyModel]() as client:
            with pytest.raises(httpx.RequestError):
                await client.get('/test', MyModel)


@pytest.mark.asyncio
async def test_get_invalid_format(mock_load_config):

    with mock.patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = mock.MagicMock()
        mock_get.return_value.json.return_value = "invalid data" 
        mock_get.return_value.raise_for_status = mock.MagicMock()

        async with ApiClient[MyModel]() as client:
            with pytest.raises(ValueError, match="Unexpected response data format"):
                await client.get('/test', MyModel)


@pytest.mark.asyncio
async def test_get_parsing_error(mock_load_config):

    with mock.patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = mock.MagicMock()
        mock_get.return_value.json.return_value = {'invalid_key': 'value'} 
        mock_get.return_value.raise_for_status = mock.MagicMock()

        async with ApiClient[MyModel]() as client:
            with pytest.raises(TypeError):
                await client.get('/test', MyModel)
