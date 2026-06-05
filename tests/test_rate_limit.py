import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_request_under_limit(
    rate_limited_client: AsyncClient,
):
    for _ in range(5):
        response = await rate_limited_client.get("/hello")
        assert response.status_code == 200


@pytest.mark.anyio
async def test_rate_limit_exceeded(rate_limited_client: AsyncClient):
    # Make 10 requests to consume the tokens
    for _ in range(10):
        response = await rate_limited_client.get("/hello")
        assert response.status_code == 200

    # The 11th request should be rate limited
    response = await rate_limited_client.get("/hello")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}


@pytest.mark.anyio
async def test_tokens_refill_after_wait(rate_limited_client: AsyncClient):
    for _ in range(10):
        response = await rate_limited_client.get("/hello")
        assert response.status_code == 200

    response = await rate_limited_client.get("/hello")
    assert response.status_code == 429

    await asyncio.sleep(3)
    response = await rate_limited_client.get("/hello")
    assert response.status_code == 200
