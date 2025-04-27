import logging
import os
import subprocess

import tldextract
from dynaconf import settings

logger = logging.getLogger(__name__)

project_root_dir = settings['project_root_dir']


def get_nested_values_file(chart_name, repository_url, chart_version, cwd):
    '''
    helm show values prometheus-community/kube-prometheus-stack > values.yaml
    '''
    subdomain = tldextract.extract(repository_url).subdomain
    helm_repo_name = subdomain
    helm_command = [
        "helm",
        "show",
        "values",
        f"{helm_repo_name}/{chart_name}",
        "--version",
        chart_version,
    ]

    try:
        with open(os.path.join(cwd, f"{helm_repo_name}_{chart_name}_values.yaml"), 'w') as f:
            subprocess.run(helm_command, stdout=f, stderr=subprocess.PIPE, check=True, cwd=cwd)
        logger.info(f"Getting {chart_name} values.yaml successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")


def get_nested_chart_file(chart_name, repository_url, chart_version, cwd):
    '''
    helm show chart prometheus-community/kube-prometheus-stack > values.yaml
    '''
    subdomain = tldextract.extract(repository_url).subdomain
    helm_repo_name = subdomain
    helm_command = [
        "helm",
        "show",
        "chart",
        f"{helm_repo_name}/{chart_name}",
        "--version",
        chart_version,
    ]

    try:
        with open(os.path.join(cwd, f"{helm_repo_name}_{chart_name}_chart.yaml"), 'w') as f:
            subprocess.run(helm_command, stdout=f, stderr=subprocess.PIPE, check=True, cwd=cwd)
        logger.info(f"Getting {chart_name} chart.yaml successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
