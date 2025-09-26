import os
import uuid
from fastapi import UploadFile
from typing import Optional
from exts.logururoute.business_logger import logger


class FileUtils:
    @staticmethod
    def get_upload_dir() -> str:
        """获取上传目录"""
        upload_dir = "static/uploads/damage_images"
        logger.info(f"创建上传目录: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"上传目录创建成功: {upload_dir}")
        return upload_dir

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """生成唯一文件名"""
        logger.info(f"生成文件名，原始文件名: {original_filename}")
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        logger.info(f"生成的唯一文件名: {unique_filename}")
        return unique_filename

    @staticmethod
    async def save_upload_file(file: UploadFile, directory: str, filename: str) -> str:
        """保存上传文件"""
        logger.info(f"保存文件到: {directory}/{filename}")
        file_path = os.path.join(directory, filename)

        try:
            # 读取文件内容
            logger.info("开始读取文件内容")
            content = await file.read()
            logger.info(f"文件内容大小: {len(content)} bytes")

            # 直接使用同步方式写入
            logger.info("开始写入文件")
            with open(file_path, "wb") as out_file:
                out_file.write(content)
            logger.info(f"文件保存成功: {file_path}")

            return file_path
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise

    @staticmethod
    async def save_damage_image(image: UploadFile) -> Optional[str]:
        """保存病害图片"""
        logger.info("开始保存病害图片")

        if not image:
            logger.warning("没有提供图片文件")
            return None

        logger.info(
            f"图片文件信息: filename={image.filename}, content_type={image.content_type}"
        )

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if image.content_type not in allowed_types:
            error_msg = f"不支持的图片格式: {image.content_type}，仅支持 JPEG 和 PNG"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("开始读取文件内容")
        try:
            # 读取文件内容一次，用于大小检查和保存
            content = await image.read()
            logger.info(f"文件读取成功，大小: {len(content)} bytes")
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            raise

        # 检查文件大小 (例如: 最大 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if len(content) > max_size:
            error_msg = f"图片文件大小超过限制: {len(content)} bytes > {max_size} bytes"
            logger.error(error_msg)
            raise ValueError("图片文件大小不能超过5MB")

        logger.info("文件大小检查通过")

        # 生成文件名和保存路径
        logger.info("生成文件名和保存路径")
        upload_dir = FileUtils.get_upload_dir()
        filename = FileUtils.generate_filename(image.filename)
        file_path = os.path.join(upload_dir, filename)

        logger.info(f"准备保存到: {file_path}")

        # 使用同步方式保存文件内容
        try:
            logger.info("开始写入文件")
            with open(file_path, "wb") as out_file:
                out_file.write(content)
            logger.info("文件写入成功")
        except Exception as e:
            logger.error(f"文件写入失败: {str(e)}")
            raise

        # 返回相对路径用于数据库存储
        relative_path = os.path.join("damage_images", filename)
        logger.info(f"文件保存完成，返回路径: {relative_path}")

        return relative_path
