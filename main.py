import boto3
import os
from botocore.exceptions import ClientError
import rembg
from PIL import Image
from fastapi import FastAPI
app = FastAPI()

# Initialize the S3 client
BUCKET_NAME = 'YOUR_BUCKET_NAME'
s3_client = boto3.client(
    's3',
    aws_access_key_id="YOUR_ACCESS_KEY",
    aws_secret_access_key="YOUR_SECRET",
    region_name='us-east-1'
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/download")
async def download_file(file_name: str | None):
    response = s3_client.download_file('s3-imageprocess506', f'input/{file_name}', f'{file_name}')
    if response:
        return {"statusCode": 200, "message": "Image downloaded successfully"}
    else:
        return {"statusCode": 500, "message": "Error downloading image at @app.get(/download)"}


@app.get("/upload")
async def upload_file(file_name: str | None):
    response = s3_client.upload_file(f'{file_name}', 's3-imageprocess506', f'output/{file_name}')
    if response is None:
        return {"statusCode": 200, "message": "Image uploaded successfully"}
    else:
        return {"statusCode": 500, "message": "Error uploading image at @app.get(/upload)"}

@app.get("/process")
async def process_image(File_name: str | None):
    """
    Remove background from image using rembg
    Steps to remove background:
    1. Read input image
    2. Save it to local directory
    3. Remove background
    4. Save output image to local directory
    5. Upload output image to S3 bucket
    """

    # Download and save input image
    await download_file(File_name)
    # Process image
    input_path = f'{File_name}'
    output_path = f'/{File_name}'
    try:
        # Read input image
        input_image = Image.open(input_path)

        # Remove background
        """
        def remove(data: bytes | Image | ndarray,
           alpha_matting: bool = False,
           alpha_matting_foreground_threshold: int = 240,
           alpha_matting_background_threshold: int = 10,
           alpha_matting_erode_size: int = 10,
           session: BaseSession | None = None,
           only_mask: bool = False,
           post_process_mask: bool = False,
           bgcolor: tuple[int, int, int, int] | None = None,
           force_return_bytes: bool = False,
           *args: Any | None,
           **kwargs: Any | None) -> bytes | Image | ndarra
        """
        model_name = "isnet-general-use"
        session = rembg.new_session(model_name)
        output_image = rembg.remove(data=input_image,
                                    session=session)

        # Save to output path
        output_image.save(File_name, 'PNG')
        # Upload output image
        if await upload_file(File_name) == {"statusCode": 200, "message": "Image uploaded successfully"}:
            #Delete the image on local directory
            os.remove(input_path)
            return {"statusCode": 200, "message": "Image processed and uploaded successfully"}

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return False
    # Upload output image




def list_files_in_bucket(bucket_name: str):
    """
    List files in an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket.

    Returns:
    dict: The response from S3 listing the objects, or None if an error occurred.
    """
    try:
        return s3_client.list_objects_v2(Bucket=bucket_name)
    except ClientError:
        return None
