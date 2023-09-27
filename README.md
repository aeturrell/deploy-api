# deploy-api

An example API deployment using Google Cloud Compute and Terraform.

## Instructions

### Setup

Download and install [terraform](https://developer.hashicorp.com/terraform/downloads).

`main.tf` is the main terraform file. It lists the API services that we'll use from Google. There are four blocks:

1. terraform metadata
2. provider region and project information
3. a block representing the storage bucket API
4. a block representing the container registry API

`.terraform.version` contains the version of terraform you're using (run `terraform --version` to check).

`variables.tf` contains information on all of the variables you wish to declare openly, eg

```text
variable "region" {
  type = string
  description = "Region for GCP resources"
  default = "europe-west6"
}
```

encodes the region variable.

Ensure you have the Google CLI installed. Go to 

 and authenticated. Once you have downloaded and installed it, run gcloud init to set it up. This is the point at which your computer becomes trusted to do things to your GCP account.

