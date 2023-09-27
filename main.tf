terraform {
    required_version = ">=1.5"
    backend "local" {}
    required_providers {
        google = {
            source = "hashicorp/google"
        }
    }
}

provider "google" {
    project = var.project_id
    region = var.region
    credentials = file("secrets/google_key.json")
}

# Artifact registry for containers
resource "google_artifact_registry_repository" "deploy-api-container-registry" {
  location      = var.region
  repository_id = var.registry_id
  format        = "DOCKER"
}

variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "artifactregistry.googleapis.com",
    "run.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = var.project_id
  service = each.key
}
