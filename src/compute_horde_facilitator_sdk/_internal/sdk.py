import abc
import typing

import httpx

from compute_horde_facilitator_sdk._internal.signature import Signer, signature_to_headers
from compute_horde_facilitator_sdk._internal.typing import JSONDict, JSONType

BASE_URL = "https://facilitator.computehorde.io/api/v1/"


HTTPClientType = typing.TypeVar("HTTPClientType", bound=httpx.Client | httpx.AsyncClient)
HTTPResponseType = typing.TypeVar("HTTPResponseType", bound=httpx.Response | typing.Awaitable[httpx.Response])


class JobStatus(typing.TypedDict, total=False):
    uuid: str
    status: str
    stdout: str
    output_download_url: str


class FacilitatorClientBase(abc.ABC, typing.Generic[HTTPClientType, HTTPResponseType]):
    def __init__(
        self,
        token: str,
        base_url: str = BASE_URL,
        signer: Signer | None = None,
    ):
        self.base_url = base_url
        self.token = token
        self.signer = signer
        self.client: HTTPClientType = self._get_client()

    @abc.abstractmethod
    def _get_client(self) -> HTTPClientType:
        raise NotImplementedError

    def _prepare_request(
        self,
        method: str,
        url: str,
        *,
        json: JSONType | None = None,
        params: dict[str, str | int] | None = None,
    ) -> HTTPResponseType:
        request = self.client.build_request(method=method, url=url, json=json, params=params)
        if self.signer:
            signature = self.signer.signature_for_request(
                request.method, str(request.url), headers=dict(request.headers), json=json
            )
            signature_headers = signature_to_headers(signature)
            request.headers.update(signature_headers)

        return typing.cast(HTTPResponseType, self.client.send(request, follow_redirects=True))

    def _get_jobs(self, page: int = 1, page_size: int = 10) -> HTTPResponseType:
        return self._prepare_request("GET", "/jobs/", params={"page": page, "page_size": page_size})

    def _get_job(self, job_uuid: str) -> HTTPResponseType:
        return self._prepare_request("GET", f"/jobs/{job_uuid}/")

    def _create_raw_job(self, raw_script: str, input_url: str = "") -> HTTPResponseType:
        data: JSONDict = {"raw_script": raw_script, "input_url": input_url}
        return self._prepare_request("POST", "/job-raw/", json=data)

    def _create_docker_job(
        self,
        docker_image: str,
        args: str = "",
        env: dict[str, str] | None = None,
        use_gpu: bool = False,
        input_url: str = "",
    ) -> HTTPResponseType:
        data: JSONDict = {
            "docker_image": docker_image,
            "args": args,
            "env": env or {},  # type: ignore # mypy doesn't acknowledge dict[str, str] | None as subtype of JSONDict
            "use_gpu": use_gpu,
            "input_url": input_url,
        }
        return self._prepare_request("POST", "/job-docker/", json=data)


class FacilitatorClient(FacilitatorClientBase[httpx.Client, httpx.Response]):
    def _get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, headers={"Authorization": f"Token {self.token}"})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.client.close()

    def handle_response(self, response: httpx.Response) -> JSONType:
        response.raise_for_status()
        return response.json()

    def get_jobs(self, page: int = 1, page_size: int = 10) -> JSONType:
        return self.handle_response(self._get_jobs(page, page_size))

    def get_job(self, job_uuid: str) -> JobStatus:
        response = self.handle_response(self._get_job(job_uuid))
        return typing.cast(JobStatus, response)

    def create_raw_job(self, raw_script: str, input_url: str = "") -> JobStatus:
        response = self.handle_response(self._create_raw_job(raw_script, input_url))
        return typing.cast(JobStatus, response)

    def create_docker_job(
        self,
        docker_image: str,
        args: str = "",
        env: dict[str, str] | None = None,
        use_gpu: bool = False,
        input_url: str = "",
    ) -> JobStatus:
        response = self.handle_response(
            self._create_docker_job(
                docker_image=docker_image,
                args=args,
                env=env,
                use_gpu=use_gpu,
                input_url=input_url,
            )
        )
        return typing.cast(JobStatus, response)


class AsyncFacilitatorClient(FacilitatorClientBase[httpx.AsyncClient, typing.Awaitable[httpx.Response]]):
    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, headers={"Authorization": f"Token {self.token}"})

    async def handle_response(self, response: typing.Awaitable[httpx.Response]) -> JSONType:
        awaited_response = await response
        awaited_response.raise_for_status()
        return awaited_response.json()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    async def get_jobs(self, page: int = 1, page_size: int = 10) -> JSONType:
        return await self.handle_response(self._get_jobs(page=page, page_size=page_size))

    async def get_job(self, job_uuid: str) -> JobStatus:
        response = await self.handle_response(self._get_job(job_uuid=job_uuid))
        return typing.cast(JobStatus, response)

    async def create_raw_job(self, raw_script: str, input_url: str = "") -> JobStatus:
        response = await self.handle_response(self._create_raw_job(raw_script=raw_script, input_url=input_url))
        return typing.cast(JobStatus, response)

    async def create_docker_job(
        self,
        docker_image: str,
        args: str = "",
        env: dict[str, str] | None = None,
        use_gpu: bool = False,
        input_url: str = "",
    ) -> JobStatus:
        response = await self.handle_response(
            self._create_docker_job(
                docker_image=docker_image,
                args=args,
                env=env,
                use_gpu=use_gpu,
                input_url=input_url,
            )
        )
        return typing.cast(JobStatus, response)
