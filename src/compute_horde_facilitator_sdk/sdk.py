from typing import Any

import httpx


def acquire_token(base_url: str, username: str, password: str) -> str:
    with httpx.Client() as client:
        response = client.post(f"{base_url}/api-token-auth/", data={"username": username, "password": password})
    response.raise_for_status()
    return response.json()["token"]


async def async_acquire_token(base_url: str, username: str, password: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{base_url}/api-token-auth/", data={"username": username, "password": password})
    response.raise_for_status()
    return response.json()["token"]


class FacilitatorClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Token {token}"})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_jobs(self, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        response = self.client.get("/jobs/", params={"page": page, "page_size": page_size})
        response.raise_for_status()
        return response.json()

    def get_job(self, job_uuid: str) -> dict[str, Any]:
        response = self.client.get(f"/jobs/{job_uuid}/")
        response.raise_for_status()
        return response.json()

    def create_raw_job(self, raw_script: str, input_url: str = "") -> dict[str, Any]:
        data = {"raw_script": raw_script, "input_url": input_url}
        response = self.client.post("/job-raw/", json=data)
        response.raise_for_status()
        return response.json()

    def create_docker_job(
        self, docker_image: str, args: str = "", env: dict[str, str] = {}, use_gpu: bool = False, input_url: str = ""
    ) -> dict[str, Any]:
        data = {
            "docker_image": docker_image,
            "args": args,
            "env": env,
            "use_gpu": use_gpu,
            "input_url": input_url,
        }
        response = self.client.post("/job-docker/", json=data)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()


class AsyncFacilitatorClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Token {token}"})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_jobs(self, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        response = await self.client.get("/jobs/", params={"page": page, "page_size": page_size})
        response.raise_for_status()
        return response.json()

    async def get_job(self, job_uuid: str) -> dict[str, Any]:
        response = await self.client.get(f"/jobs/{job_uuid}/")
        response.raise_for_status()
        return response.json()

    async def create_raw_job(self, raw_script: str, input_url: str = "") -> dict[str, Any]:
        data = {"raw_script": raw_script, "input_url": input_url}
        response = await self.client.post("/job-raw/", json=data)
        response.raise_for_status()
        return response.json()

    async def create_docker_job(
        self, docker_image: str, args: str = "", env: dict[str, str] = {}, use_gpu: bool = False, input_url: str = ""
    ) -> dict[str, Any]:
        data = {"docker_image": docker_image, "args": args, "env": env, "use_gpu": use_gpu, "input_url": input_url}
        response = await self.client.post("/job-docker/", json=data)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
