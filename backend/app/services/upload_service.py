import os
import uuid
import imghdr
from flask import current_app
from werkzeug.datastructures import FileStorage
from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

class UploadService:
    @staticmethod
    def save_image(file: FileStorage, subfolder: str = 'recipes') -> tuple[str | None, str | None]:
        """
        Save an uploaded image file.
        Returns (url_path, error_message).
        """
        # Validate extension
        filename = file.filename
        if not filename or '.' not in filename:
            return None, '无效的文件名'

        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return None, f'不支持的文件类型: .{ext}，仅允许 {", ".join(ALLOWED_EXTENSIONS)}'

        # Validate size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_SIZE:
            return None, f'文件大小不能超过 {MAX_SIZE // 1024 // 1024}MB'

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}_{int(__import__('time').time())}.{ext}"

        # Ensure directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_dir, unique_name)
        file.save(filepath)

        # Validate image content and optimize
        try:
            img = Image.open(filepath)
            img.verify()
            # Re-open after verify
            img = Image.open(filepath)
            # Resize if too large
            if max(img.width, img.height) > 2000:
                img.thumbnail((2000, 2000), Image.LANCZOS)
            img.save(filepath, optimize=True, quality=85)
        except Exception:
            os.remove(filepath)
            return None, '无效的图片文件'

        url_path = f"/uploads/{subfolder}/{unique_name}"
        return url_path, None

    @staticmethod
    def delete_image(filepath: str) -> bool:
        """Delete an image file."""
        try:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath.replace('/uploads/', '', 1))
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False
