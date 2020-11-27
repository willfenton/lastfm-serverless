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

  lifecycle_rule {
    id      = aws_athena_named_query.create_table_scrobbles.name
    prefix  = "${aws_athena_named_query.create_table_scrobbles.name}/"
    enabled = true

    expiration {
      days = 30
    }
  }

  lifecycle_rule {
    id      = aws_athena_named_query.create_view_top_albums.name
    prefix  = "${aws_athena_named_query.create_view_top_albums.name}/"
    enabled = true

    expiration {
      days = 30
    }
  }

  lifecycle_rule {
    id      = aws_athena_named_query.get_top_albums.name
    prefix  = "${aws_athena_named_query.get_top_albums.name}/"
    enabled = true

    expiration {
      days = 30
    }
  }

  lifecycle_rule {
    id      = "unsaved_athena_queries"
    prefix  = "Unsaved/"
    enabled = true

    expiration {
      days = 30
    }
  }
}
