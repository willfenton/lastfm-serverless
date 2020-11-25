resource "aws_athena_database" "database" {
  name   = "${lower(replace(var.project_name, "-", "_"))}_database"
  bucket = aws_s3_bucket.athena_bucket.bucket
}

resource "aws_athena_named_query" "create_table_scrobbles" {
  name     = "${lower(replace(var.project_name, "-", "_"))}_create_table_scrobbles"
  database = aws_athena_database.database.name
  query    = <<EOF
CREATE EXTERNAL TABLE IF NOT EXISTS ${aws_athena_database.database.name}.scrobbles (
  `track_name` string,
  `album_name` string,
  `artist_name` string,
  `unix_timestamp` int,
  `album_art_url` string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "escapeChar" = "\\")
LOCATION 's3://lastfm-serverless-data/scrobbles/'
TBLPROPERTIES ('has_encrypted_data'='false');
EOF
}

resource "aws_athena_named_query" "create_view_top_albums" {
  name     = "${lower(replace(var.project_name, "-", "_"))}_create_view_top_albums"
  database = aws_athena_database.database.name
  query    = <<EOF
CREATE
        OR REPLACE VIEW "top_albums" AS
WITH query1 (album_name, artist_name, count, num_tracks, first_uts, last_uts) AS
    (SELECT album_name,
         artist_name,
         COUNT(*),
         COUNT(DISTINCT track_name),
         MIN(unix_timestamp),
         MAX(unix_timestamp)
    FROM scrobbles
    GROUP BY  album_name, artist_name ), query2 (album_name, artist_name, track_name, count, album_art_url) AS
    (SELECT album_name,
         artist_name,
         track_name,
         COUNT(*),
         album_art_url
    FROM scrobbles
    GROUP BY  album_name, artist_name, track_name, album_art_url ), query3 (album_name, artist_name, track_name, album_count, track_count, num_tracks, rank, first_uts, last_uts, album_art_url) AS
    (SELECT q2.album_name,
         q2.artist_name,
         q2.track_name,
         q1.count,
         q2.count,
         q1.num_tracks,
         ROW_NUMBER() OVER(PARTITION BY q2.album_name,
         q2.artist_name
    ORDER BY  q2.count DESC), q1.first_uts, q1.last_uts, q2.album_art_url
    FROM ( query1 q1
    JOIN query2 q2
        ON q1.album_name = q2.album_name
            AND q1.artist_name = q2.artist_name ) )
SELECT album_name,
         artist_name,
         track_name,
         album_count,
         track_count,
         num_tracks,
         first_uts,
         last_uts,
         album_art_url
FROM query3
WHERE rank = 1
        AND num_tracks > 2
EOF
}
