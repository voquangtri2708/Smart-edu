import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app

def setup_cloudinary():
    """Configure Cloudinary from app config"""
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )

def upload_image(file_data, folder="avatars"):
    """
    Upload an image to Cloudinary
    
    Args:
        file_data: Base64 encoded image data
        folder: Folder to store image in Cloudinary (default: avatars)
        
    Returns:
        The URL of the uploaded image
    """
    try:
        # Configure Cloudinary
        setup_cloudinary()
        
        # Upload image to Cloudinary
        result = cloudinary.uploader.upload(
            file_data,
            folder=folder,
            resource_type="image"
        )
        
        # Return the secure URL
        return result.get('secure_url')
    except Exception as e:
        # Log the error and return None
        print(f"Error uploading image to Cloudinary: {str(e)}")
        return None

def delete_image(public_id):
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Public ID of the image to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Configure Cloudinary
        setup_cloudinary()
        
        # Delete the image
        result = cloudinary.uploader.destroy(public_id)
        
        # Check if deletion was successful
        return result.get('result') == 'ok'
    except Exception as e:
        # Log the error and return False
        print(f"Error deleting image from Cloudinary: {str(e)}")
        return False 