# deploy-api

An example API deployment. The project makes use of Google Cloud, Terraform, and FastAPI.

Google Cloud provides a place to stow containers and a way to deploy the API. FastAPI is a package that makes writing astoundingly high-quality APIs embarrassingly quick. Terraform is a tool that helps you do "infrastructure as code", ie to build, change, and version control cloud resources safely and efficiently.

## Initial Setup

### First Steps

Download and install [terraform](https://developer.hashicorp.com/terraform/downloads). Do the same for [poetry](https://python-poetry.org/) and ensure you have a version of Python installed.

If you've cloned this repository, the `.gitignore` file has a lot of useful bits in already that will help protect information you do not want to share with others.

### Creating a Google Project

Get a [Google Cloud Account](https://console.cloud.google.com/).

Ensure you have the [Google CLI installed](https://cloud.google.com/sdk/docs/install-sdk) and authenticated: once you have downloaded and installed it, run `gcloud init` to set it up. Then run `gcloud auth login` to ensure you are logged into your account. With these steps done, you can make changes to your Google Cloud account from the command line.

We're now going to create a project on the command line.

```bash
gcloud projects create YOUR-PROJECT-ID
```

You may wish to add some numbers to the end of the project name to ensure it is unique. (Note that it needs to be the same as the project ID in your `terraform.tfvars` file, which we'll come to later.)

Next up, switch the Google Cloud CLI to use this specific project:

```bash
gcloud config set project YOUR-PROJECT-ID
```

Now we have to go to the [Google Cloud Console](https://console.cloud.google.com/). Navigate to the relevant project, and then create a new Service Account under IAM. The current [URL is here](https://console.cloud.google.com/iam-admin/serviceaccounts). A service account can be used to manage access to Google Cloud services.

In the new service account, click on Actions then Manage keys. Create a new key which will be downloaded as a JSON file—do not put it under version control, but do safe it in the `secrets` subdirectory with the name `google_key.json`.

You'll also need to set up billing, which can be found under billing.

### Terraforming Google Cloud Components

Terraform is a cross-cloud provider way of specifying resources. We're going to use it to create a new Google project and create an Artifact Registry within it. (This registry is eventually where we will push a docker image of our app.)

`main.tf` is the main terraform file. It lists the API services that we'll use from Google, and also enables them too. There are a few distinct blocks:

1. terraform metadata
2. provider region and project information
3. a block representing the container registry API
4. (last two blocks) code that enables the registry and cloud run APIs

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

Next, run `terraform plan`, which will think through what you've asked for in `main.tf`.

Finally, to create the GCP resources, it's `terraform apply`. If successful, you will see a message saying: "Apply complete! Resources: 3 added, 0 changed, 0 destroyed."

An alternative to using the last block of `main.tf` to enable the APIs is to use the Google Cloud CLI.

```bash
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
```

You can check what services you have enabled with `gcloud services list --enabled`.

## Python and the API

### Setup

Run `poetry config virtualenvs.in-project true` to make virtual environments be installed in the local project folder.

Run `poetry install` to install the Python env.

Note that, for reasons of good practice, this repository uses `pre-commit`. You can run this using `poetry run pre-commit run --all-files`.

### Prepping the data

There are a few Python scripts in a folder called `etl`. These perform the following functions:

- `etl/extract.py` — downloads deaths data by geography from this ONS page, which has Excel files for each year. The script downloads them all.
- `etl/transform.py` - this takes downloaded files, opens them, finds the relevant sheets, cleans them, and stacks them in a tidy format in a parquet file. Challenges are:
  - Worksheet names change over time
  - File formats change (the file extension)
  - New data may be added in a new file, if the new data refer to January, or added into an existing file, if the month they refer to is not January
- `etl/main.py` — this is a script that calls the extract and transform scripts in order.

To create the data we'll be serving up later, it's

```bash
poetry run python etl/main.py
```

### Launching the API locally (optional)

To use FastAPI locally to serve up your API, you'll need to have installed the Python environment (via **poetry**)

```bash
poetry run uvicorn app.api:app --reload
```

where app is the folder, `api.py` is the script, and app is the FastAPI application defined in `api.py`. This serves up an API in the form: `/year/{YEAR-OF-INTEREST}/geo_code/{GEO-CODE-OF-INTEREST}`. For example, if FastAPI is running on http://0.0.0.0:8080, then http://0.0.0.0:8080/year/2021/geo_code/E08000007 would serve up the 2021 deaths data for Stockport (which has UK local authority geographic code E08000007). You can also try http://0.0.0.0:8080/docs.

## Deploying the API to the cloud

We already enabled the cloud run API using terraform. The plan now is: build a docker container with everything needed to serve up the API in, build the docker file into an image, upload the image to the artifact registry we created on Google Cloud, and then serve the API on Google Cloud Run. First, we need to ensure our env is reproducible in a docker file.

### Building the docker image

You can make poetry (which this project uses) work in docker files but it can go wrong, so it's easier to run:

```bash
poetry export -f requirements.txt --output requirements.txt
```

And have the docker file use the `requirements.txt`. Note that, because of this method of prepping the docker file, `requirements.txt` has been added to the `.gitignore` file.

### Testing the containerised API locally (optional)

You can check that your Dockerfile works locally first if you wish. To do this, run

```bash
docker build --pull --rm -f "Dockerfile" -t deploy-api:latest "."
```

to build it and then

```bash
docker run --rm -it -p 8080:8080/tcp deploy-api:latest
```

to run it. You should get a message in the terminal that includes a HTTP address that you can go to (this isn't really on the internet, it's coming from inside the house). Click on that and you should see your API load up. For example, if it's on http://0.0.0.0:8080 head to http://0.0.0.0:8080/docs to check that the docs have loaded and try out the API.

### Building the docker image for Google Cloud Run

Now we run into a complication. I'm using a Mac, which is on arm64 architecture, aka Apple Silicon. Most cloud services are Linux-based, which typically use amd64 chips. Naively building an image locally, and pushing it to Google Cloud, would result in an image that won't actually run on Google's architecture. So we need to use a multi-platform build, or just build to target a specific architecture.

You need to use

```bash
docker buildx create --name mybuilder --bootstrap --use
```

to create a builder to take on image construction. Then, the magic command to build the image and push it to your google repo is:

```bash
docker buildx build --file Dockerfile \
  --platform linux/amd64 \
  --builder mybuilder \
  --progress plain \
  --build-arg DOCKER_REPO=REGION-docker.pkg.dev/PROJECT-ID/REPOSITORY-NAME/ \
  --pull --push \
  --tag REGION-docker.pkg.dev/PROJECT-ID/REPOSITORY-NAME/deploy-api:latest .
```

where REPOSITORY-NAME is the name of the `registry_id` variable in `terraform.tfvars`. Note the "platform" argument.

### Deploy

Now deploy the app with

`gcloud run deploy app --image REGION-docker.pkg.dev/PROJECT-ID/REPOSITORY-NAME/deploy-api:latest --region REGION --platform managed --allow-unauthenticated`

All being well, you should get a message saying

```text
Deploying container to Cloud Run service [app] in project [PROJECT-ID] region [REGION]
✓ Deploying new service... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
```

## Here's one I built earlier!

You can see the running version here: [https://app-qdvgjvqwza-nw.a.run.app](https://app-qdvgjvqwza-nw.a.run.app)

## Final Thoughts

The commoditisation of cloud services, and the great developments in Python as a language, have made it far, far easier to create APIs. Although there are a few components to get your head around here, it's amazing how quickly you can create a working API.

It's worth noting that, if all your API is doing is serving up tabular data, there's a much easier way to to this (even though building an API with FastAPI is so easy). You can use the excellent [datasette](https://datasette.io/). You can see a worked example of using it to [serve up some data here](https://github.com/aeturrell/datasette_particulate_matter). It seems like FastAPI would be much more useful with more unusually structured data, when you need to interact with data by writing as well as reading, or when you need cloud run to do other activities too (like pull from a Google database). NB: you could configure GitHub Actions to update a datasette instance, so simply updating a database on a schedule is entirely possible with datasette.
