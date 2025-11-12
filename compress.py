from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import mysql.connector

load_dotenv()
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(connect_str)

original_container = "original"
thumbnail_container = "thumbnail"

original_client = blob_service_client.get_container_client(original_container)
thumbnail_client = blob_service_client.get_container_client(thumbnail_container)


db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

original_blobs = original_client.list_blobs()
thumbnail_blob_names = [blob.name for blob in thumbnail_client.list_blobs()]

for blob in original_blobs:
    thumb_name = f"thumb_{blob.name}"
    if thumb_name in thumbnail_blob_names:
        print(f"Skipping already processed file: {blob.name}")
        continue
    print(f"Compressing: {blob.name}")

    downloader = original_client.download_blob(blob.name)
    image_data = downloader.readall()


    image = Image.open(BytesIO(image_data))
    image.thumbnail((150, 150))

    output_stream = BytesIO()
    image.save(output_stream, format="PNG")
    output_stream.seek(0)


    thumbnail_client.upload_blob(name=thumb_name, data=output_stream, overwrite=True)

    thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{thumbnail_container}/{thumb_name}"
    original_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{original_container}/{blob.name}"

    cursor.execute(
        "UPDATE images SET thumbnailURL=%s WHERE originalURL=%s",
        (thumbnail_url, original_url)
    )
    db.commit()

print("All images processed.")

