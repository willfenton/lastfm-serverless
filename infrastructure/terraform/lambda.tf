resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.project_name}-lambda-policy"
  path        = "/"
  description = "IAM policy for Lambda allowing logging to Cloudwatch (log group must already exist) and accessing Secrets Manager secrets"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    },
    {
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "${aws_secretsmanager_secret.api_key.arn}",
      "Effect": "Allow"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3::*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_cloudwatch_log_group" "update_range_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.update_range.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_function" "update_range" {
  function_name = "${var.project_name}-update-range"
  role          = aws_iam_role.lambda_role.arn

  s3_bucket         = aws_s3_bucket_object.lambda_code.bucket
  s3_key            = aws_s3_bucket_object.lambda_code.key
  s3_object_version = aws_s3_bucket_object.lambda_code.version_id
  source_code_hash = "${filebase64sha256(aws_s3_bucket_object.lambda_code.source)}-${aws_iam_role.lambda_role.arn}"
  handler           = "update_range.lambda_handler"
  runtime           = "python3.8"
  timeout           = 900

  environment {
    variables = {
      aws_region  = var.aws_region,
      lastfm_user = var.lastfm_user,
      secret_name = aws_secretsmanager_secret.api_key.name,
      data_bucket = aws_s3_bucket.data_bucket.bucket
    }
  }
}

resource "aws_cloudwatch_log_group" "daily_update_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.daily_update.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_function" "daily_update" {
  function_name = "${var.project_name}-daily-update"
  role          = aws_iam_role.lambda_role.arn

  s3_bucket         = aws_s3_bucket_object.lambda_code.bucket
  s3_key            = aws_s3_bucket_object.lambda_code.key
  s3_object_version = aws_s3_bucket_object.lambda_code.version_id
  source_code_hash = "${filebase64sha256(aws_s3_bucket_object.lambda_code.source)}-${aws_iam_role.lambda_role.arn}"
  handler           = "daily_update.lambda_handler"
  runtime           = "python3.8"
  timeout           = 900

  environment {
    variables = {
      aws_region  = var.aws_region,
      timezone    = var.timezone,
      update_lambda_name = aws_lambda_function.update_range.function_name
    }
  }
}
