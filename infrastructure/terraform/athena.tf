resource "aws_athena_database" "database" {
  name   = "${lower(replace(var.project_name, "-", "_"))}_database"
  bucket = aws_s3_bucket.athena_bucket.bucket
}
