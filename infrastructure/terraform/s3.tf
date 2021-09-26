resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "${var.project_name}-lambda-code"
  acl    = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "expire_old_code"
    enabled = true

    noncurrent_version_expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_bucket.bucket
  key    = "lambda-code.zip"
  source = "../../build/lambda-code.zip"
  etag   = filemd5("../../build/lambda-code.zip")
}

resource "aws_s3_bucket" "athena_bucket" {
  bucket = "${var.project_name}-athena-output"
  acl    = "private"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.project_name}-data"
  acl    = "private"
}

resource "aws_s3_bucket" "public_bucket" {
  bucket = "${var.project_name}-public"
  acl    = "private"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = var.cors_origins
    expose_headers  = []
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_policy" "public_bucket_policy" {
  bucket = aws_s3_bucket.public_bucket.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression's result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource = [
          "${aws_s3_bucket.public_bucket.arn}/*",
        ]
        Condition : {
          StringLike : {
            "aws:Referer" : [for origin in var.cors_origins : "${origin}/*"]
          }
        }
      }
    ]
  })
}