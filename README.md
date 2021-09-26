# lastfm-serverless

![UI](https://user-images.githubusercontent.com/31602935/134795676-c7f70201-b20f-4855-ac5c-d43a57ddc234.png)

## What is this?

[Check it out!](https://willfenton.dev/lastfm-serverless/)

This is a project I built to explore my music listening history. It displays your top albums in a grid, and you can click on an album to see some cool stats like how many times you've listened to it, the first and last times you listened to it, and a graph of how often you listened to it over time. The music listening data all comes from [last.fm](https://www.last.fm), an awesome service which automatically logs your listening history.

It's not done yet either, I want to add much more in terms of data visualization in the future.

## How does it work?

### Frontend

The frontend is a web app that loads a CSV containing all of your last.fm scrobbles, and displays them all. It is written in [TypeScript](https://www.typescriptlang.org/) and it uses [Vue.js](https://vuejs.org/), [Chart.js](https://www.chartjs.org/), and [Papa Parse](https://www.papaparse.com/).

### Backend

The backend resides in [AWS](https://aws.amazon.com/) and is entirely serverless, making it very cheap to run (less than $1/month). Scrobbles (records of listening to song X at time Y) are downloaded from the [last.fm API](https://www.last.fm/api) in a [Lambda](https://aws.amazon.com/lambda/) function, and are stored as JSON in an [S3](https://aws.amazon.com/s3/) bucket. Every day, new scrobbles are automatically downloaded. The CSV the frontend uses is generated using [Athena](https://aws.amazon.com/athena/).

## Setup

If you just want your last.fm account added, reach out to me and I'll see what I can do. But if you want to run your own instance, here's a setup guide. I think it should work but there's a chance I missed something.

### Pre-requisites

1. An AWS account
2. [AWS CLI](https://aws.amazon.com/cli/)
3. [Terraform](https://www.terraform.io/) CLI
4. A last.fm account
5. A last.fm API key

### Steps

1. Fork the repo
2. From `infrastructure/terraform`, initialize terraform with `terraform init`
3. Set terraform variables in `infrastructure/terraform/variables.tf`. You should set them in a `infrastructure/terraform/terraform.tfvars` file, something like this:
```
lastfm_usernames = ["willfenton14"]
lastfm_api_key   = "<API KEY>"
cors_origins     = ["https://willfenton.dev", "https://willfenton.github.io"]  // your website
```
4. From the project root, run the build script `build.sh` to build and package the AWS Lambda code
5. Create the AWS resources by running `terraform apply` from `/infrastructure/terraform`
6. Run the `lastfm-serverless-query-athena` lambda function (from the AWS console or CLI) with an event like this to create the AWS Athena table for your last.fm account:
```
{
  "lastfm_usernames": ["willfenton14"],
  "queries": ["create_table"]
}
```
7. Run the `lastfm-serverless-get-all-scrobbles` lambda function with an event like this to download all of your scrobbles using the last.fm API:
```
{
  "lastfm_username": "willfenton14"
}
```
8. Run the `lastfm-serverless-query-athena` lambda function again with an event like this to generate a CSV with all your scrobbles:
```
{
  "lastfm_usernames": ["willfenton14"],
  "queries": ["get_all_scrobbles"]
}
```
At this point you should have a CSV with all your scrobbles in your `lastfm-serverless-public` S3 bucket. If not, something went wrong.

9. Change the data URL in `src/web/index.ts` to point to your S3 bucket
10. Deploy the web app to GitHub pages by running `npm run deploy` from the project root
11. Load the web app and hope it works! Be sure to add `?username=<your last.fm username>` to the end of the URL.

---

It's a lot of setup, but now you should be able to leave it alone indefinitely. Every day, lambda functions are automatically triggered to download your scrobbles for the day and update the CSV, so no more manual steps required!

If you want to destroy everything, run `terraform destroy` from `infrastructure/terraform` (although you will probably have to empty some S3 buckets and destroy some Athena tables manually).
