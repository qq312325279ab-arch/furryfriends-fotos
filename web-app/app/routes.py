from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Image, db
from app import db
import os
from azure.storage.blob import BlobServiceClient
import uuid
from PIL import Image as PILImage
import io

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.gallery'))
    return render_template('index.html')

@main.route('/gallery')
@login_required
def gallery():
    # Get all images, ordered by newest first
    images = Image.query.order_by(Image.created_at.desc()).all()
    return render_template('gallery.html', images=images)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
            
        file = request.files['file']
        caption = request.form.get('caption', '')
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
            
        if file:
            # Save image info first
            new_image = Image(
                caption=caption,
                ownerUserID=current_user.userID,
                file_name=file.filename
            )
            
            db.session.add(new_image)
            db.session.commit()
            
            # Upload to Azure Blob Storage
            original_url, thumbnail_url = upload_to_azure_blob(file, new_image.imageID)
            
            # Update image URLs
            new_image.originalURL = original_url
            new_image.thumbnailURL = thumbnail_url
            db.session.commit()
            
            flash('Image uploaded successfully!')
            return redirect(url_for('main.gallery'))
            
    return render_template('upload.html')

def upload_to_azure_blob(file, image_id):
    # Connect to Azure Blob Storage
    connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Generate unique filenames
    file_extension = file.filename.split('.')[-1].lower()
    original_filename = f"{image_id}_original.{file_extension}"
    thumbnail_filename = f"{image_id}_thumbnail.jpg"
    
    # Upload original image
    original_container = "originals"
    original_blob_client = blob_service_client.get_blob_client(
        container=original_container,
        blob=original_filename
    )
    
    file.stream.seek(0)
    original_blob_client.upload_blob(file.stream)
    
    # Generate and upload thumbnail
    thumbnail_container = "thumbnails"
    thumbnail_blob_client = blob_service_client.get_blob_client(
        container=thumbnail_container,
        blob=thumbnail_filename
    )
    
    # Create thumbnail
    file.stream.seek(0)
    image = PILImage.open(file.stream)
    image.thumbnail((150, 150))
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    thumbnail_blob_client.upload_blob(img_byte_arr)
    
    return original_blob_client.url, thumbnail_blob_client.url
