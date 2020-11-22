resource "aws_secretsmanager_secret" "api_key" {
  name = "${var.project_name}-api-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "example" {
  secret_id = aws_secretsmanager_secret.api_key.id
  secret_string = jsonencode({
    api_key = var.lastfm_api_key
  })
}
