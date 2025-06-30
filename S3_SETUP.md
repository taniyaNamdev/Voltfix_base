# AWS S3 Setup for VoltFix

This guide will help you set up AWS S3 for storing all images in your VoltFix application.

## Prerequisites

1. **AWS Account**: You need an AWS account
2. **AWS CLI** (optional but recommended): For easier management
3. **Python packages**: Already installed (`django-storages`, `boto3`, `python-dotenv`)

## Step 1: Create S3 Bucket

1. **Log into AWS Console**
2. **Go to S3 Service**
3. **Create a new bucket**:
   - Bucket name: `voltfix-media` (or your preferred name)
   - Region: Choose closest to your users
   - Block all public access: **Uncheck** (we need public read access)
   - Bucket versioning: Optional
   - Tags: Add tags for organization

## Step 2: Configure Bucket Permissions

### Option A: Using Bucket Policy (Recommended)

Add this bucket policy to your S3 bucket:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

### Option B: Using CORS Configuration

Add this CORS configuration to your bucket:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## Step 3: Create IAM User

1. **Go to IAM Service** in AWS Console
2. **Create a new user**:
   - Username: `voltfix-s3-user`
   - Access type: Programmatic access
3. **Attach policies**:
   - Create custom policy or use `AmazonS3FullAccess` (for development)
   - For production, create a more restrictive policy

## Step 4: Get Access Keys

1. **After creating the IAM user**, download the CSV file
2. **Note down**:
   - Access Key ID
   - Secret Access Key

## Step 5: Configure Environment Variables

1. **Create a `.env` file** in your project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=Voltdix_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# AWS S3 Settings
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=voltfix-media
AWS_S3_REGION_NAME=us-east-1

# Social Authentication Settings
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

2. **Replace the values** with your actual credentials

## Step 6: Test the Setup

1. **Run Django check**:
   ```bash
   python manage.py check
   ```

2. **Test file upload** through admin panel:
   - Go to `/admin/`
   - Try uploading an image to a service category or product
   - Check if the file appears in your S3 bucket

## Step 7: Upload Existing Files (Optional)

If you have existing files in your local `media/` folder:

```bash
# Install AWS CLI
pip install awscli

# Configure AWS CLI
aws configure

# Upload existing files
aws s3 sync media/ s3://your-bucket-name/media/
```

## File Structure in S3

Your S3 bucket will have this structure:

```
your-bucket-name/
├── media/
│   ├── profile_pics/
│   │   ├── user1.jpg
│   │   └── default.jpg
│   ├── products/
│   │   ├── product1.jpg
│   │   └── product2.png
│   └── services/
│       ├── service1.jpg
│       └── service2.png
└── static/
    ├── css/
    ├── js/
    └── images/
```

## Security Best Practices

1. **Use IAM roles** instead of access keys in production
2. **Restrict bucket permissions** to only what's needed
3. **Enable bucket versioning** for backup
4. **Set up CloudFront** for better performance
5. **Monitor costs** regularly

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Check IAM user permissions
2. **Bucket not found**: Verify bucket name and region
3. **CORS errors**: Add CORS configuration to bucket
4. **Files not public**: Check bucket policy

### Debug Commands:

```bash
# Test S3 connection
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.exists('test.txt')
```

## Production Deployment

For production:

1. **Use environment variables** in your deployment platform
2. **Set `USE_S3=True`** in production
3. **Use CloudFront** for CDN
4. **Monitor costs** and set up billing alerts
5. **Regular backups** of your S3 bucket

## Cost Optimization

1. **Use S3 Intelligent Tiering** for cost savings
2. **Set up lifecycle policies** for old files
3. **Compress images** before upload
4. **Use appropriate storage classes**

---

**Note**: Keep your AWS credentials secure and never commit them to version control! 