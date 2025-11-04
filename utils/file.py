"""
@File: file_utils.py
@Description: 通用文件上传工具模块

---
如何为您的新项目进行定制 (How to Customize for Your Project)
---
要将此工具类移植到新项目（例如：电商、博客、ERP系统），请按以下步骤操作：

1.  修改 FileCategory (文件类别枚举):
    这是最重要的一步。删除或修改当前桥梁系统相关的类别 (如 OTHER, DESIGN_DOC 等)。
    添加您自己项目所需的业务类别。

    示例（用于一个电商项目）:
    class FileCategory(str, Enum):
        USER_AVATAR = "user_avatar"      # 用户头像
        PRODUCT_IMAGE = "product_image"  # 商品图片
        INVOICE_PDF = "invoice_pdf"      # 发票PDF
        SUPPORT_TICKET = "support_ticket" # 工单附件

2.  更新 FILE_TYPE_CONFIGS (文件类型配置映射):
    -   为 FileCategory 中定义的 每一个 新类别添加一个配置项。
    -   键 (Key) 是枚举成员 (如 FileCategory.USER_AVATAR)。
    -   值 (Value) 是一个 FileTypeConfig 实例，您需要在此处定义：
        -   allowed_mime_types: 允许的MIME类型 (!!! 非常重要，用于核心安全验证)
        -   allowed_extensions: 允许的文件后缀 (用于辅助验证)
        -   max_size_mb: 最大文件大小 (MB)
        -   upload_subdir: 存放该类文件的子目录 (将自动创建在 BASE_UPLOAD_DIR 下)
        -   description: 描述 (用于日志和错误信息)

    示例（对应上面的电商项目）:
    FILE_TYPE_CONFIGS: Dict[FileCategory, FileTypeConfig] = {
        FileCategory.USER_AVATAR: FileTypeConfig(
            allowed_mime_types=["image/jpeg", "image/png", "image/webp"],
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"],
            max_size_mb=2,
            upload_subdir="avatars",
            description="用户头像"
        ),
        FileCategory.PRODUCT_IMAGE: FileTypeConfig(
            allowed_mime_types=["image/jpeg", "image/png", "image/webp"],
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"],
            max_size_mb=5,
            upload_subdir="products",
            description="商品图片"
        ),
        FileCategory.INVOICE_PDF: FileTypeConfig(
            allowed_mime_types=["application/pdf"],
            allowed_extensions=[".pdf"],
            max_size_mb=10,
            upload_subdir="invoices",
            description="发票PDF"
        ),
        # ... 其他配置 ...
    }

3.  修改 BASE_UPLOAD_DIR
    默认上传根目录是 static/uploads。如果您的项目需要不同的根目录 (例如 media_files 或从环境变量读取)，
    请修改 FileUtils.BASE_UPLOAD_DIR 静态变量。
"""

import os
import uuid
from dataclasses import dataclass
from enum import Enum
from fastapi import UploadFile
from typing import Optional, List, Dict
from exts.logururoute.business_logger import logger


class FileCategory(str, Enum):
    """文件类别枚举"""

    DOCTOR_DOCUMENT = "doctor_document"  # 医生文档
    DOCTOR_AVATAR = "doctor_avatar"  # 医生头像
    OTHER = "other"  # 其他资料


@dataclass
class FileTypeConfig:
    """文件类型配置"""

    allowed_mime_types: List[str]  # 允许的MIME类型
    allowed_extensions: List[str]  # 允许的文件扩展名
    max_size_mb: int  # 最大文件大小(MB)
    upload_subdir: str  # 上传子目录
    description: str  # 描述


# 文件类型配置映射
FILE_TYPE_CONFIGS: Dict[FileCategory, FileTypeConfig] = {
    FileCategory.DOCTOR_DOCUMENT: FileTypeConfig(
        allowed_mime_types=["application/pdf", "application/msword"],
        allowed_extensions=[".pdf", ".doc", ".docx"],
        max_size_mb=10,
        upload_subdir="doctor_documents",
        description="医生文档",
    ),
    FileCategory.DOCTOR_AVATAR: FileTypeConfig(
        allowed_mime_types=["image/jpeg", "image/png", "image/webp"],
        allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"],
        max_size_mb=2,
        upload_subdir="doctor_avatars",
        description="医生头像",
    ),
    FileCategory.OTHER: FileTypeConfig(
        allowed_mime_types=["*/*"],
        allowed_extensions=["*"],
        max_size_mb=10,
        upload_subdir="others",
        description="其他资料",
    ),
}


class FileUtils:
    BASE_UPLOAD_DIR = "static/uploads"

    @staticmethod
    def get_upload_dir(file_category: FileCategory = FileCategory.OTHER) -> str:
        """
        获取上传目录

        Args:
            file_category: 文件类别，默认为病害图片

        Returns:
            上传目录的完整路径
        """
        config = FILE_TYPE_CONFIGS.get(file_category)
        if not config:
            raise ValueError(f"不支持的文件类别: {file_category}")

        upload_dir = os.path.join(FileUtils.BASE_UPLOAD_DIR, config.upload_subdir)
        logger.info(f"创建上传目录: {upload_dir} ({config.description})")
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
    def validate_file(
        file: UploadFile, file_category: FileCategory, content: bytes
    ) -> None:
        """
        验证文件是否符合要求

        Args:
            file: 上传的文件对象
            file_category: 文件类别
            content: 文件内容字节

        Raises:
            ValueError: 文件不符合要求时抛出异常
        """
        config = FILE_TYPE_CONFIGS.get(file_category)
        if not config:
            raise ValueError(f"不支持的文件类别: {file_category}")

        # 检查文件类型（MIME类型）
        if file.content_type not in config.allowed_mime_types:
            logger.error(
                f"不支持的文件格式: {file.content_type}，"
                f"{config.description}仅支持: {', '.join(config.allowed_mime_types)}"
            )
            raise ValueError(
                f"不支持的文件格式: {file.content_type}，"
                f"{config.description}仅支持: {', '.join(config.allowed_extensions)}"
            )

        # 检查文件扩展名
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in config.allowed_extensions:
            logger.error(
                f"不支持的文件扩展名: {file_extension}，"
                f"{config.description}仅支持: {', '.join(config.allowed_extensions)}"
            )
            raise ValueError(
                f"不支持的文件扩展名，{config.description}仅支持: {', '.join(config.allowed_extensions)}"
            )

        # 检查文件大小
        max_size = config.max_size_mb * 1024 * 1024  # 转换为字节
        if len(content) > max_size:
            logger.error(
                f"文件大小超过限制: {len(content)} bytes > {max_size} bytes "
                f"({config.max_size_mb}MB)"
            )
            raise ValueError(f"{config.description}大小不能超过{config.max_size_mb}MB")

        logger.info(
            f"文件验证通过: {file.filename}, "
            f"类型: {file.content_type}, "
            f"大小: {len(content)} bytes"
        )

    @staticmethod
    async def save_file(
        file: UploadFile, file_category: FileCategory = FileCategory.OTHER
    ) -> Optional[str]:
        """
        文件保存方法

        Args:
            file: 上传的文件对象
            file_category: 文件类别

        Returns:
            文件的相对路径，用于数据库存储；如果文件为空则返回 None

        Raises:
            ValueError: 文件验证失败时抛出异常
        """
        if not file:
            logger.warning("没有提供文件")
            return None

        config = FILE_TYPE_CONFIGS.get(file_category)
        if not config:
            raise ValueError(f"不支持的文件类别: {file_category}")

        logger.info(
            f"开始保存{config.description}: "
            f"filename={file.filename}, content_type={file.content_type}"
        )

        # 读取文件内容
        try:
            content = await file.read()
            logger.info(f"文件读取成功，大小: {len(content)} bytes")
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            raise

        # 验证文件
        FileUtils.validate_file(file, file_category, content)

        # 生成文件名和保存路径
        upload_dir = FileUtils.get_upload_dir(file_category)
        filename = FileUtils.generate_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)

        logger.info(f"准备保存到: {file_path}")

        # 保存文件
        try:
            with open(file_path, "wb") as out_file:
                out_file.write(content)
            logger.info(f"文件保存成功: {file_path}")
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            raise

        # 返回相对路径
        relative_path = os.path.join(config.upload_subdir, filename)
        logger.info(f"文件保存完成，返回相对路径: {relative_path}")

        return relative_path
