import os
import shutil
import tarfile
import time

from dynaconf import settings

from .download_chart_values_file import get_nested_chart_file, get_nested_values_file
from .ecr_docker_image_registry import *
from .ecr_helm_chart_registry import *
from .ecr_helm_chart_registry import login_ecr_helm_chart_registry, push_chart_to_ecr
from .extract_dependencies_from_chart import extract as extract_charts
from .extract_images_from_values import extract as extract_images
from .pull_charts_with_specified_version import add_helm_repo, pull_chart

project_root_dir = settings['project_root_dir']


def find_helm_tgz_files(path):
    tgz_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.tgz'):
                tgz_files.append(os.path.join(root, file))
    return tgz_files


class HelmBuilder:
    def __init__(self, source_chart_name, source_chart_repo):
        self.dependent_charts_metadata = []
        self.source_chart_name = source_chart_name
        self.source_chart_repo = source_chart_repo
        self.cwd = os.path.join(project_root_dir, source_chart_name)

    def extract(self):
        dependencies = extract_charts(self.source_chart_name, self.source_chart_repo)
        self.dependent_charts_metadata.extend(dependencies)
        return self

    def add_helm_repo(self):
        for _, repository, _ in self.dependent_charts_metadata:
            add_helm_repo(repository_url=repository)
        return self

    def pull_charts(self):
        for name, repository, version in self.dependent_charts_metadata:
            if name == self.source_chart_name:
                pull_chart(chart_name=name, repository_url=repository, chart_version=version, cwd=self.cwd)
        return self

    def push_charts_to_ecr(self):
        tgz_files = find_helm_tgz_files(self.cwd)
        for tgz in tgz_files:
            login_ecr_helm_chart_registry(tgz)
            push_chart_to_ecr(tgz, cwd=self.cwd)
        else:
            shutil.rmtree(os.path.join(project_root_dir, self.source_chart_name, self.source_chart_name))
        return self

    def get_nested_values_files(self):
        for name, repository, version in self.dependent_charts_metadata:
            get_nested_values_file(chart_name=name, repository_url=repository, chart_version=version, cwd=self.cwd)
        return self

    def get_nested_chart_files(self):
        for name, repository, version in self.dependent_charts_metadata:
            get_nested_chart_file(chart_name=name, repository_url=repository, chart_version=version, cwd=self.cwd)
        return self

    def update_source_helm_chart_yaml(self):
        '''
        lock nested dependencies version
        '''
        source_helm_chart_tar_path = ""
        for filename in os.listdir(os.path.join(project_root_dir, self.source_chart_name)):
            if filename.startswith(self.source_chart_name) and filename.endswith('.tgz'):
                source_helm_chart_tar_path = os.path.join(project_root_dir, self.source_chart_name, filename)

        with tarfile.open(source_helm_chart_tar_path, "r") as tar:
            tar.extractall(path=os.path.join(project_root_dir, self.source_chart_name))

        shutil.copy(
            os.path.join(project_root_dir, self.source_chart_name, "Chart.yaml"),
            os.path.join(project_root_dir, self.source_chart_name, self.source_chart_name, "Chart.yaml"),
        )

        helm_command = ["helm", "dependency", "update"]

        try:
            subprocess.run(helm_command, check=True, cwd=os.path.join(self.cwd, self.source_chart_name))
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred: {e}")

        helm_command = ["helm", "package", self.source_chart_name]

        try:
            subprocess.run(helm_command, check=True, cwd=self.cwd)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred: {e}")

        return self


class ImageBuilder:
    def __init__(self, source_chart_name):
        self.dependent_images_metadata = []
        self.source_chart_name = source_chart_name

    def extract(self):
        images = extract_images(self.source_chart_name)
        self.dependent_images_metadata.extend(images)
        return self

    def docker_pull(self):
        try:
            for image in self.dependent_images_metadata:
                pull_images(image)
        except ValueError:
            self.dependent_images_metadata.remove(image)
            self.dependent_images_metadata.append(image.split(":")[0])
        return self

    def ecr_docker_login(self):
        login_ecr_docker_image_registry()
        return self

    def ecr_docker_tag(self):
        for image in self.dependent_images_metadata:
            tag_ecr_image(image)
        return self

    def ecr_docker_push(self):
        for image in self.dependent_images_metadata:
            push_to_ecr_docker_image_registry(image)
            time.sleep(1)
        return self
