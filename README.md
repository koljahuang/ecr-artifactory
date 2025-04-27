## Target 🚀
Upload dependent helm package and involved nested images to **private ecr registry**.

## Precautions 👀
Execution environment with access to resources outside the GFW.

## Instruction Manual 📖

#### 1. Install poetry
For more details, please refer to the [Poetry 1.8](https://python-poetry.org/docs/1.8/) official documentation.

#### 2. Create a virtual environment and activate it
```sh
cd /path/to/project
poetry config virtualenvs.in-project true
poetry shell
```

#### 3. Install dependencies
```sh
poetry install --no-root
```

#### 4. Upload all nested helm charts and images of specified helm chart name

1. Project Structure Overview
    ```
    .
    ├── main.py
    ├── pyproject.toml
    ├── actions
    │   ├── download_chart_values_file.py
    │   ├── ...
    ├── ...
    └── settings.toml
    ```
2. Let's take installing the aws-load-balancer-controller as an example.
    ```sh
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    helm search repo eks/aws-load-balancer-controller --versions
    ```
3. Add *helm chart folder* in the root directory of the project
    ```
    .
    ├── main.py
    ├── aws-load-balancer-controller 👈 Add a folder here
    ├── pyproject.toml
    ├── actions
    │   ├── download_chart_values_file.py
    │   ├── ...
    ├── ...
    └── settings.toml
    ```
4. Create `Chart.yaml` of this helm chart
    ```sh
    helm show chart eks/aws-load-balancer-controller --version 1.12.0 > aws-load-balancer-controller/Chart.yaml
    ```

5. Configure credentials
    ```sh
    cat << EOF > settings.toml
    [development]
    AWS_ACCOUNT = 'aws account'
    AWS_REGION = 'aws region'
    AWS_PROFILE = 'profile name'
    EOF
    ```

6. Trigger the action chains to achieve targets
    ```python
    python3 main.py -sc aws-load-balancer-controller -scr https://aws.github.io/eks-charts
    ```
