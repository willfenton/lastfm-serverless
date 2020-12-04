resource "aws_cloudwatch_event_rule" "daily_update" {
  name                = "${var.project_name}-daily-update-cron"
  description         = "Triggers the daily update lambda every day at 7:10 AM UTC (12:10 AM MST)"
  schedule_expression = "cron(10 7 * * ? *)"
}

resource "aws_cloudwatch_event_target" "daily_update" {
  rule      = aws_cloudwatch_event_rule.daily_update.name
  target_id = "lambda"
  arn       = aws_lambda_function.daily_update.arn
  input = jsonencode({
    "lastfm_usernames" = var.lastfm_usernames
  })
}

resource "aws_lambda_permission" "cloudwatch_daily_update_lambda_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daily_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_update.arn
}

resource "aws_cloudwatch_event_rule" "daily_queries" {
  name                = "${var.project_name}-daily-queries"
  description         = "Triggers the athena query lambda every day at 7:15 AM UTC (12:15 AM MST)"
  schedule_expression = "cron(15 7 * * ? *)"
}

resource "aws_cloudwatch_event_target" "daily_queries" {
  rule      = aws_cloudwatch_event_rule.daily_queries.name
  target_id = "lambda"
  arn       = aws_lambda_function.query_athena.arn
  input = jsonencode({
    "lastfm_usernames" = var.lastfm_usernames,
    "queries"          = ["get_top_albums", "get_month_counts"]
  })
}

resource "aws_lambda_permission" "cloudwatch_daily_queries_lambda_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.query_athena.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_queries.arn
}
