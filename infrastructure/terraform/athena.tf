resource "aws_athena_database" "database" {
  name   = "${lower(replace(var.project_name, "-", "_"))}_database"
  bucket = aws_s3_bucket.athena_bucket.bucket
}

resource "aws_athena_named_query" "create_table" {
  name      = "${lower(replace(var.project_name, "-", "_"))}_create_table_query"
  database  = aws_athena_database.database.name
  query     = <<EOF
CREATE EXTERNAL TABLE IF NOT EXISTS ${aws_athena_database.database.name}.scrobbles (
  `track_name` string,
  `album_name` string,
  `artist_name` string,
  `unix_timestamp` int
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "escapeChar" = "\\")
LOCATION 's3://lastfm-serverless-data/scrobbles/'
TBLPROPERTIES ('has_encrypted_data'='false');
EOF
}

resource "aws_athena_named_query" "top_albums" {
  name      = "${lower(replace(var.project_name, "-", "_"))}_top_albums_query"
  database  = aws_athena_database.database.name
  query     = <<EOF
SELECT album_name, artist_name, MIN(unix_timestamp), MAX(unix_timestamp), COUNT(*)
FROM scrobbles
GROUP BY album_name, artist_name
ORDER BY COUNT(*) DESC
LIMIT 200;
EOF
}
