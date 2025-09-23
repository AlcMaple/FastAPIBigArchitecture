import os
import uuid
from fastapi import UploadFile
from typing import Optional
import aiofiles


class FileUtils:
    @staticmethod
    def get_upload_dir() -> str:
        """获取上传目录"""
        upload_dir = "static/uploads/damage_images"
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """生成唯一文件名"""
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        return unique_filename

    @staticmethod
    async def save_upload_file(file: UploadFile, directory: str, filename: str) -> str:
        """保存上传文件"""
        file_path = os.path.join(directory, filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        return file_path

    @staticmethod
    async def save_damage_image(image: UploadFile) -> Optional[str]:
        """保存病害图片"""
        if not image:
            return None

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if image.content_type not in allowed_types:
            raise ValueError("不支持的图片格式，仅支持 JPEG 和 PNG")

        # 检查文件大小 (例如: 最大 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        content = await image.read()
        if len(content) > max_size:
            raise ValueError("图片文件大小不能超过5MB")

        # 重置文件指针
        await image.seek(0)

        # 生成文件名和保存路径
        upload_dir = File.get_upload_dir()
        filename = File.generate_filename(image.filename)

        # 保存文件
        file_path = await File.save_upload_file(image, upload_dir, filename)

        # 返回相对路径用于数据库存储
        relative_path = os.path.join("damage_images", filename)
        return relative_path
