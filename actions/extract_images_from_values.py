import logging
import os

import yaml
from dynaconf import settings

logger = logging.getLogger(__name__)

project_root_dir = settings['project_root_dir']


def extract(source_chart_name):
    source_chart_dir = os.path.join(project_root_dir, source_chart_name)
    values_yaml_path = os.path.join(project_root_dir, source_chart_name, 'values.yaml')

    images = set()

    if os.path.exists(source_chart_dir):
        logger.debug(f"Source chart named {source_chart_name} is located")
        if not os.path.exists(values_yaml_path):
            logger.warning(f"Source chart named {source_chart_name} can be located. But it is an empty file")
    else:
        logger.warning(f"Source chart named {source_chart_name} can not be located. Pls add metadata of source chart manually as a format of folder")

    app_version_mapping = {}

    for root, _, files in os.walk(source_chart_dir):
        for file in files:
            chart_name = file.split('_chart')[0]
            if file.endswith("chart.yaml"):
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, 'r') as f:
                    chart_yaml_content = f.read()
                    chart_data = yaml.safe_load(chart_yaml_content)
                if chart_name.startswith("grafana"):
                    app_version_mapping[chart_name] = chart_data["appVersion"]
                else:
                    if chart_data.get("appVersion"):
                        if not chart_data["appVersion"].startswith("v"):
                            app_version_mapping[chart_name] = "v" + chart_data["appVersion"]
                        else:
                            app_version_mapping[chart_name] = chart_data["appVersion"]
    logger.debug(f'app_version_mapping: {app_version_mapping}')

    for root, _, files in os.walk(source_chart_dir):
        for file in files:
            if not file.endswith("values.yaml"):
                continue
            logger.debug("-" * 20)
            logger.debug(file)
            chart_name = file.split('_values')[0]
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                values_yaml_content = f.read()
                values_data = yaml.safe_load(values_yaml_content)

            def extract_images(d):
                if isinstance(d, dict):
                    for key, value in d.items():
                        if key.lower().endswith('image'):
                            if not isinstance(value, dict):
                                continue
                            if value.get('tag'):
                                if value.get('registry'):
                                    images.add(f"{value['registry']}/{value['repository']}:{value['tag']}")
                                else:
                                    images.add(f"{value['repository']}:{value['tag']}")
                            else:
                                if value.get("repository"):
                                    if app_version_mapping.get(chart_name):
                                        if value.get('registry'):
                                            images.add(f"{value['registry']}/{value['repository']}:{app_version_mapping.get(chart_name)}")
                                        else:
                                            images.add(f"{value['repository']}:{app_version_mapping.get(chart_name)}")
                        else:
                            try:
                                extract_images(value)
                            except KeyError:
                                pass

            try:
                extract_images(values_data)
            except KeyError:
                pass

    disable_images = ['ghcr.io/prometheus-community/windows-exporter:v0.29.2', 'quay.io/minio/minio:RELEASE.2024-04-18T19-09-19Z', 'quay.io/minio/mc:RELEASE.2024-04-18T16-45-29Z']
    for i in disable_images:
        try:
            images.remove(i)
        except KeyError:
            continue
    logger.debug(f"metadata of images:\n{images}")
    return images
