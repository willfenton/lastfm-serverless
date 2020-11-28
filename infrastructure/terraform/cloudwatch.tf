resource "aws_cloudwatch_event_rule" "daily_update" {
  name                = "${var.project_name}-daily-update-cron"
  description         = "Triggers the daily update lambda every day at 7:10 AM UTC (12:10 AM MST)"
  schedule_expression = "cron(10 7 * * ? *)"
}

resource "aws_cloudwatch_event_target" "daily_update" {
  rule      = aws_cloudwatch_event_rule.daily_update.name
  target_id = "lambda"
  arn       = aws_lambda_function.daily_update.arn
  input     = jsonencode({
    "lastfm_usernames"=var.lastfm_usernames
  })
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daily_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_update.arn
}
