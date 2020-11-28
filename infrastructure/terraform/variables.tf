variable "aws_region" {
}

variable "aws_profile" {
}

variable "project_name" {
  default = "lastfm-serverless"
}

variable "lastfm_usernames" {
}

variable "lastfm_api_key" {
}

// scrobble updates will be from midnight to midnight for the specified timezone
variable "timezone" {
}

// sites that can use the API
// https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
variable "cors_origins" {
}

# allows for replacing strings in album names
# e.g. removing "(Deluxe)" from album names
# {
#   "string_in_album_name"="string_to_replace_with"
# }
variable "album_replacements" {
}

# allows for replacing strings in artist names
# e.g. "JAY Z" -> "JAY-Z"
variable "artist_replacements" {
}

# allows for replacing strings in track names
variable "track_replacements" {
}
