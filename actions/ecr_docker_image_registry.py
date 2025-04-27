import logging
import subprocess

from dynaconf import settings

logger = logging.getLogger(__name__)

image_registry = ["quay.io", "docker.io", "registry.k8s.io", "ghcr.io", "public.ecr.aws"]


def pull_images(image):
    docker_command = [
        # "sudo",
        "docker",
        "pull",
        "--platform",
        "linux/amd64",
        image,
    ]
    try:
        subprocess.run(docker_command, check=True)
        logger.info(f"Pulling {image} successfully.")
    except subprocess.CalledProcessError as e:
        raise ValueError


def login_ecr_docker_image_registry():
    docker_command = (
        f"aws ecr get-login-password --region cn-northwest-1 --profile adminnx | docker login --username AWS --password-stdin {settings.AWS_ACCOUNT}.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
    )
    logger.debug(docker_command)

    try:
        result = subprocess.run(docker_command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def tag_ecr_image(image):
    source_image = image
    if image.split('/')[0] in image_registry:
        tmp = image.split('/')[1:]
        if 'library' in tmp:
            tmp.remove('library')
        image = '/'.join(tmp)

    docker_command = f"docker tag {source_image} {settings.AWS_ACCOUNT}.dkr.ecr.cn-northwest-1.amazonaws.com.cn/{image}"
    try:
        subprocess.run(docker_command, shell=True, check=True)
        logger.info(f"Tag {image} successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def push_to_ecr_docker_image_registry(image):
    if image.split('/')[0] in image_registry:
        tmp = image.split('/')[1:]
        if 'library' in tmp:
            tmp.remove('library')
        image = '/'.join(tmp)

    # create repo first
    repository_name = image.split(':')[0]
    try:
        cmd = f"aws ecr create-repository --repository-name {repository_name} --region {settings.AWS_REGION} --profile {settings.AWS_PROFILE} "
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            logger.info(f"{result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"ecr repo: {repository_name} existed")
    except Exception as e:
        pass

    docker_command = f"docker push {settings.AWS_ACCOUNT}.dkr.ecr.cn-northwest-1.amazonaws.com.cn/{image}"
    try:
        subprocess.run(docker_command, shell=True, check=True)
        logger.info(f"Push {image} to ecr container registry successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
