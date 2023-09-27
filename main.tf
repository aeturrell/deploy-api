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
