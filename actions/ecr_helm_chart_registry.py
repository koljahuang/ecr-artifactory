import logging
import subprocess

from dynaconf import settings

logger = logging.getLogger(__name__)


def login_ecr_helm_chart_registry(chart_tgz):
    repository_name = '-'.join(chart_tgz.split('.tgz')[0].split('/')[-1].split('-')[:-1])

    # create repo first
    try:
        cmd = f"aws ecr create-repository --repository-name {repository_name} --region {settings.AWS_REGION} --profile {settings.AWS_PROFILE} "
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            logger.info(f"{result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"ecr repo existed")
    except Exception as e:
        pass

    cmd = f"aws ecr get-login-password --profile {settings.AWS_PROFILE} | helm registry login --username AWS --password-stdin {settings.AWS_ACCOUNT}.dkr.ecr.{settings.AWS_REGION}.amazonaws.com.cn"
    logger.debug(cmd)
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def push_chart_to_ecr(chart_tgz, cwd):
    cmd = ["helm", "push", chart_tgz, f"oci://{settings.AWS_ACCOUNT}.dkr.ecr.{settings.AWS_REGION}.amazonaws.com.cn"]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=cwd)
        logger.info(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e.stderr}")
