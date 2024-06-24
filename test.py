import os
import time

from compute_horde_facilitator_sdk.v1 import BittensorWalletSigner, FacilitatorClient

signer = None
# Optionally, you can sign each request with your wallet for additional security & higher execution priority.
try:
    import bittensor

    signer = BittensorWalletSigner(bittensor.wallet())
except ImportError:
    print("bittensor package not installed, skipping wallet signing")


compute_horde = FacilitatorClient(
    token=os.environ["COMPUTE_HORDE_FACILITATOR_TOKEN"],
    signer=signer,
)

job = compute_horde.create_docker_job(
    docker_image="backenddevelopersltd/gen_caption_v2",
    # The zip file will be extracted within the Docker container to the /volume directory
    input_url="https://raw.githubusercontent.com/backend-developers-ltd/ComputeHorde-examples/master/input_shapes.zip",
    use_gpu=True,
)

while True:
    job = compute_horde.get_job(job["uuid"])
    if job["status"] in ["Completed", "Failed"]:
        break
    time.sleep(10)

print(
    f'Job finished with status: {job["status"]}. Stdout is: "{job["stdout"]}",'
    f' output_url is {job["output_download_url"]}'
)
# During job execution, any files generated in the /output directory will be incorporated into the final job result,
# which can be downloaded from the url printed above. Full STDOUT and STDERR will also be there.
