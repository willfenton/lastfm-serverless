resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_origins
  }
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name = "/${aws_apigatewayv2_api.http_api.name}/logs"
  retention_in_days = 14
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id = aws_apigatewayv2_api.http_api.id
  name   = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format = jsonencode(
      {
        httpMethod     = "$context.httpMethod"
        ip             = "$context.identity.sourceIp"
        protocol       = "$context.protocol"
        requestId      = "$context.requestId"
        requestTime    = "$context.requestTime"
        responseLength = "$context.responseLength"
        routeKey       = "$context.routeKey"
        status         = "$context.status"
      }
    )
  }

  lifecycle {
    ignore_changes = [
      deployment_id
    ]
  }
}

resource "aws_apigatewayv2_route" "top_albums" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /top-albums"
  target    = "integrations/${aws_apigatewayv2_integration.get_top_albums_lambda.id}"
}

resource "aws_apigatewayv2_integration" "get_top_albums_lambda" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"

  connection_type         = "INTERNET"
  payload_format_version  = "2.0"
  integration_method      = "POST"
  integration_uri         = aws_lambda_function.api_top_albums.invoke_arn
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "allow_api_to_invoke_lambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_top_albums.arn
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/*"
}
