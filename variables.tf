variable "project_id" {
  type= string
  description = "GCS project ID"
}

variable "region" {
  type = string
  description = "Region for GCP resources"
  default = "europe-west6"
}

variable "registry_id" {
  type = string
  description = "Name of artifact registry repository."
}
