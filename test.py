import time

from compute_horde_facilitator_sdk.v1 import FacilitatorClient

computehorde = FacilitatorClient(
    token=...,
)

job = computehorde.create_docker_job(
    docker_image='backenddevelopersltd/gen_caption_v2',
    input_url='https://raw.githubusercontent.com/backend-developers-ltd/'
              'ComputeHorde-examples/master/input_shapes.zip',
    # The zip file will be extracted within the Docker container to the /volume directory
    use_gpu=True,
)

while True:
    job = computehorde.get_job(job['uuid'])
    if job['status'] in ['Completed', 'Failed']:
        break
    time.sleep(10)

print(f'Job finished with status: {job["status"]}. Stdout is: "{job["stdout"]}",'
      f' output_url is {job["output_download_url"]}')
# During job execution, any files generated in the /output directory will be incorporated into the final job result, 
# which can be downloaded from the url printed above. Full STDOUT and STDERR will also be there.
