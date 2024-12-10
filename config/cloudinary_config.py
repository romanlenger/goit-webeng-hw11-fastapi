import cloudinary
import cloudinary.uploader
import cloudinary.api


cloudinary.config(
    cloud_name="your_cloud_name",      # Замініть на ваш Cloud Name
    api_key="your_api_key",           # Замініть на ваш API Key
    api_secret="your_api_secret"      # Замініть на ваш API Secret
)