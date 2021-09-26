// set these variables in terraform.tfvars

variable "aws_region" {
  default = "us-east-1"
}

variable "aws_profile" {
  default = "default"
}

variable "project_name" {
  default = "lastfm-serverless"
}

// list of lastfm users to collect data for
variable "lastfm_usernames" {
}

variable "lastfm_api_key" {
}

// scrobble updates will be from midnight to midnight for the specified timezone
variable "timezone" {
  default = "America/Edmonton"
}

// sites that can use the API
// https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
variable "cors_origins" {
}
