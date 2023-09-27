# deploy-api

An example API deployment using Google Cloud Platform and Terraform.

The project makes use of Google Cloud, Terraform, and FastAPI.

## Instructions

### First Steps

Download and install [terraform](https://developer.hashicorp.com/terraform/downloads). Do the same for [poetry](https://python-poetry.org/) and ensure you have a version of Python installed.

### Python

Run `poetry config virtualenvs.in-project true` to make virtual environments be installed in the local project folder.

Run `poetry install` to install the Python env.

To create the data we'll be serving up later, it's

```bash
poetry run python etl/main.py
```

#### Google Project

Get a Google Cloud Account.

Ensure you have the [Google CLI installed](https://cloud.google.com/sdk/docs/install-sdk) and authenticated: once you have downloaded and installed it, run `gcloud init` to set it up. Then run `gcloud auth login` to ensure you are logged into your account. With these steps done, you can make changes to your Google Cloud account from the command line.

We're now going to create a project on the command line.

```bash
gcloud projects create YOUR-PROJECT-ID
```

You may wish to add some numbers to the end of the project name to ensure it is unique. Note that it needs to be the same as the project ID in your `terraform.tfvars` file.

Next up, switch the Google Cloud CLI to use this specific project:

```bash
gcloud config set project YOUR-PROJECT-ID
```

Now we have to go to the [Google Cloud Console](https://console.cloud.google.com/). Navigate to the relevant project, and then create a new Service Account under IAM. The current [URL is here](https://console.cloud.google.com/iam-admin/serviceaccounts). A service account can be used to manage access to Google Cloud services.

In the new service account, click on Actions then Manage keys. Create a new key which will be downloaded as a JSON file — keep it safe, and do not put it under version control.

You'll also need to set up billing, which can be found under billing.

```bash
gcloud services enable artifactregistry.googleapis.com
```

```bash
gcloud services enable run.googleapis.com
```

#### Terraform

Terraform is a cross-cloud provider way of specifying resources. We're going to use it to create a new Google project and create an Artifact Registry within it. (This registry is eventually where we will push a docker image of our app.)

`main.tf` is the main terraform file. It lists the API services that we'll use from Google. There are four blocks:

1. terraform metadata
2. provider region and project information
3. a block representing the storage bucket API
4. a block representing the container registry API

`.terraform.version` contains the version of terraform you're using (run `terraform --version` to check).

`variables.tf` provides meta-data on the variables needed in your project.

In an extra file, that is not included in this repo and which shouldn't be public, called `terraform.tfvars`, put the actual names of your Google Cloud Project variables. The contents will look like this:

```text
#  GCP settings
project_id = "YOUR PROJECT ID"
region = "YOUR REGION"

#  Artifact registry
registry_id = "YOUR ARTIFACT REGISTRY NAME"
```

There should be an entry in this file for every variable in the `variables.tf` file.

Now run `terraform init`. If successful, you should see a message saying "Terraform has been successfully initialized!".



## Building the docker image

Ensure you have the Google CLI installed. Go to

 and authenticated. Once you have downloaded and installed it, run gcloud init to set it up. This is the point at which your computer becomes trusted to do things to your GCP account.
