import argparse
import logging
import os

from dynaconf import settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

project_root_dir = os.path.dirname(__file__)
logger.info(f"The project dir: {project_root_dir}")
settings.set("PROJECT_ROOT_DIR", project_root_dir)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-sc",
    "--source-chart",
    type=str,
    help="source chart name",
    dest="source_chart_name",
    required=True,
)
parser.add_argument(
    "-scr",
    "--source-chart-repo",
    type=str,
    help="source chart repo",
    dest="source_chart_repo",
    required=True,
)
args = parser.parse_args()


def run():
    from actions.orchestration import HelmBuilder, ImageBuilder

    HelmBuilder(
        args.source_chart_name, args.source_chart_repo
    ).extract().add_helm_repo().get_nested_values_files().get_nested_chart_files().pull_charts().update_source_helm_chart_yaml().push_charts_to_ecr()

    ImageBuilder(args.source_chart_name).extract().docker_pull().ecr_docker_login().ecr_docker_tag().ecr_docker_push()


if __name__ == "__main__":
    run()
