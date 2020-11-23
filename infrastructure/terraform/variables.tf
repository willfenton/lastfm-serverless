variable "aws_region" {
}

variable "aws_profile" {
}

variable "project_name" {
  default = "lastfm-serverless"
}

variable "lastfm_user" {
}

variable "lastfm_api_key" {
}

// scrobble updates will be from midnight to midnight for the specified timezone
variable "timezone" {
}
