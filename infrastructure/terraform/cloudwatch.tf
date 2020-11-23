resource "aws_cloudwatch_event_rule" "daily_update" {
  name                = "${var.project_name}-daily-update-cron"
  description         = "Triggers the daily update lambda every day at 12:00 PM UTC (5:00 AM MST)"
  schedule_expression = "cron(0 12 * * ? *)"
}

resource "aws_cloudwatch_event_target" "daily_update" {
  rule      = aws_cloudwatch_event_rule.daily_update.name
  target_id = "lambda"
  arn       = aws_lambda_function.daily_update.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daily_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_update.arn
}
