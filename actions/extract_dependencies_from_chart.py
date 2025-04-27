import logging
import os
import sys

import yaml
from dynaconf import settings

logger = logging.getLogger(__name__)

project_root_dir = settings['project_root_dir']


def extract(source_chart_name, source_chart_repo):
    source_chart_dir = os.path.join(project_root_dir, source_chart_name)
    chart_yaml_path = os.path.join(project_root_dir, source_chart_name, 'Chart.yaml')

    if os.path.exists(source_chart_dir):
        logger.debug(f"Source chart named {source_chart_name} is located")
        if not os.path.exists(chart_yaml_path):
            logger.warning(f"Source chart named {source_chart_name} can be located. But it is an empty file")
    else:
        logger.warning(f"Source chart named {source_chart_name} can not be located. Pls add metadata of source chart manually as a format of folder")

    with open(chart_yaml_path) as f:
        chart_yaml_content = f.read()
        data = yaml.safe_load(chart_yaml_content)

        version = data.get('version', '')
        settings.set("version", version)
        logger.debug(f'version of helm chart {source_chart_name}: {settings.get("version")}')

        dependencies = data.get('dependencies', [])
        if not dependencies:
            logger.warning(f"No dependencies required for source chart named {source_chart_name}")
        result = []

        for dep in dependencies:
            if dep.get("repository"):
                dep_info = (dep.get("name"), dep.get("repository"), dep.get("version"))
                result.append(dep_info)

        source_chart_metadata = (source_chart_name, source_chart_repo, version)
        result.append(source_chart_metadata)
        logger.debug(f"metadata of dependencies:\n{result}")
        return result
