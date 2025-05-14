# Creator Marketing AI

This repository implements the following APIs to provide copy and image generation for marketing campaigns of our Financial Institutions to communicate affiliated merchants.

## Deployment Instructions

1. Create an S3 bucket in AWS:
   - Go to AWS S3 console
   - Create a new bucket
   - Enable static website hosting in the bucket properties
   - Configure the bucket policy to allow public access (if needed)

2. Create an IAM user with S3 access:
   - Go to AWS IAM console
   - Create a new user with programmatic access
   - Attach the `AmazonS3FullAccess` policy
   - Save the Access Key ID and Secret Access Key

3. Add GitHub Secrets:
   - Go to your GitHub repository
   - Navigate to Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`: Your IAM user's access key
     - `AWS_SECRET_ACCESS_KEY`: Your IAM user's secret key
     - `S3_BUCKET`: Your S3 bucket name

4. Push to main branch:
   - The workflow will automatically trigger when you push to the main branch
   - You can monitor the deployment in the Actions tab of your repository

## Manual Deployment (Using AWS CLI)

If you need to deploy manually, you can use the AWS CLI:

```bash
aws s3 sync . s3://your-bucket-name --delete
```
