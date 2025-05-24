import logging
import os
import subprocess

import tldextract
from dynaconf import settings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

project_root_dir = settings['project_root_dir']


def get_nested_values_file(chart_name, repository_url, chart_version, cwd):
    '''
    helm show values prometheus-community/kube-prometheus-stack > values.yaml
    '''
    parsed = urlparse(repository_url)
    host = parsed.netloc
    if host == 'ghcr.io':
        helm_repo_name = repository_url
        target_path = os.path.join(cwd, f"ghcr_{chart_name}_values.yaml")
    else:
        subdomain = tldextract.extract(repository_url).subdomain
        helm_repo_name = subdomain
        target_path = os.path.join(cwd, f"{helm_repo_name}_{chart_name}_values.yaml")

    helm_command = [
        "helm",
        "show",
        "values",
        f"{helm_repo_name}/{chart_name}",
        "--version",
        chart_version,
    ]

    try:
        with open(target_path, 'w') as f:
            subprocess.run(helm_command, stdout=f, stderr=subprocess.PIPE, check=True, cwd=cwd)
        logger.info(f"Getting {chart_name} values.yaml successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def get_nested_chart_file(chart_name, repository_url, chart_version, cwd):
    '''
    helm show chart prometheus-community/kube-prometheus-stack > values.yaml
    '''
    parsed = urlparse(repository_url)
    host = parsed.netloc
    if host == 'ghcr.io':
        helm_repo_name = repository_url
        target_path = os.path.join(cwd, f"ghcr_{chart_name}_values.yaml")
    else:   
        subdomain = tldextract.extract(repository_url).subdomain
        helm_repo_name = subdomain
        target_path = os.path.join(cwd, f"{helm_repo_name}_{chart_name}_chart.yaml")

    helm_command = [
        "helm",
        "show",
        "chart",
        f"{helm_repo_name}/{chart_name}",
        "--version",
        chart_version,
    ]

    try:
        with open(target_path, 'w') as f:
            subprocess.run(helm_command, stdout=f, stderr=subprocess.PIPE, check=True, cwd=cwd)
        logger.info(f"Getting {chart_name} chart.yaml successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
