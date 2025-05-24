import logging
import subprocess

import tldextract
from dynaconf import settings
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

project_root_dir = settings['project_root_dir']


def add_helm_repo(repository_url):
    parsed = urlparse(repository_url)
    host = parsed.netloc
    if host == 'ghcr.io':
        logger.info("{repository_url} is a GitHub Container Registry URL.")
        return

    subdomain = tldextract.extract(repository_url).subdomain
    helm_repo_name = subdomain

    try:
        subprocess.run(["helm", "repo", "remove", helm_repo_name], check=True)
    except Exception as e:
        pass

    helm_command = ["helm", "repo", "add", helm_repo_name, repository_url]

    try:
        subprocess.run(helm_command, check=True)
        logger.info(f"Adding helm repo `{helm_repo_name}` executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def pull_chart(chart_name, repository_url, chart_version, cwd):
    parsed = urlparse(repository_url)
    host = parsed.netloc
    if host == 'ghcr.io':
        helm_repo_name = repository_url
    else:
        subdomain = tldextract.extract(repository_url).subdomain
        helm_repo_name = subdomain

    helm_command = [
        "helm",
        "pull",
        f"{helm_repo_name}/{chart_name}",
        "--version",
        chart_version,
    ]

    print(helm_command)

    try:
        subprocess.run(helm_command, check=True, cwd=cwd)
        logger.info(f"Pulling {chart_name} successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
