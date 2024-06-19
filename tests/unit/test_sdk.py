import pytest
import pytest_asyncio


@pytest.fixture
def base_url():
    return "https://example.com"


@pytest.fixture
def token():
    return "your_token"


@pytest.fixture
def facilitator_client(apiver_module, base_url, token):
    return apiver_module.FacilitatorClient(token, base_url)


@pytest_asyncio.fixture
async def async_facilitator_client(apiver_module, base_url, token):
    async with apiver_module.AsyncFacilitatorClient(token, base_url) as client:
        yield client


def test_get_jobs(facilitator_client, httpx_mock):
    expected_response = {"results": [{"id": 1, "name": "Job 1"}, {"id": 2, "name": "Job 2"}]}
    httpx_mock.add_response(json=expected_response)
    response = facilitator_client.get_jobs()
    assert response == expected_response


def test_get_job(facilitator_client, httpx_mock):
    job_uuid = "abc123"
    expected_response = {"id": 1, "name": "Job 1"}
    httpx_mock.add_response(json=expected_response)
    response = facilitator_client.get_job(job_uuid)
    assert response == expected_response


def test_create_raw_job(facilitator_client, httpx_mock):
    raw_script = "echo 'Hello, World!'"
    input_url = "https://example.com/input"
    expected_response = {"id": 1, "status": "queued"}
    httpx_mock.add_response(json=expected_response)
    response = facilitator_client.create_raw_job(raw_script, input_url)
    assert response == expected_response


def test_create_docker_job(facilitator_client, httpx_mock):
    docker_image = "my-image"
    args = "--arg1 value1"
    env = {"ENV_VAR": "value"}
    use_gpu = True
    input_url = "https://example.com/input"
    expected_response = {"id": 1, "status": "queued"}
    httpx_mock.add_response(json=expected_response)
    response = facilitator_client.create_docker_job(docker_image, args, env, use_gpu, input_url)
    assert response == expected_response


@pytest.mark.asyncio
async def test_async_get_jobs(async_facilitator_client, httpx_mock):
    expected_response = {"results": [{"id": 1, "name": "Job 1"}, {"id": 2, "name": "Job 2"}]}
    httpx_mock.add_response(json=expected_response)
    response = await async_facilitator_client.get_jobs()
    assert response == expected_response


@pytest.mark.asyncio
async def test_async_get_job(async_facilitator_client, httpx_mock):
    job_uuid = "abc123"
    expected_response = {"id": 1, "name": "Job 1"}
    httpx_mock.add_response(json=expected_response)
    response = await async_facilitator_client.get_job(job_uuid)
    assert response == expected_response


@pytest.mark.asyncio
async def test_async_create_raw_job(async_facilitator_client, httpx_mock):
    raw_script = "echo 'Hello, World!'"
    input_url = "https://example.com/input"
    expected_response = {"id": 1, "status": "queued"}
    httpx_mock.add_response(json=expected_response)
    response = await async_facilitator_client.create_raw_job(raw_script, input_url)
    assert response == expected_response


@pytest.mark.asyncio
async def test_async_create_docker_job(async_facilitator_client, httpx_mock):
    docker_image = "my-image"
    args = "--arg1 value1"
    env = {"ENV_VAR": "value"}
    use_gpu = True
    input_url = "https://example.com/input"
    expected_response = {"id": 1, "status": "queued"}
    httpx_mock.add_response(json=expected_response)
    response = await async_facilitator_client.create_docker_job(docker_image, args, env, use_gpu, input_url)
    assert response == expected_response
