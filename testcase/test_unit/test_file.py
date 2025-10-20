"""
单元测试 - 文件工具函数

utils/file.py
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO

from utils.file import FileUtils


class TestFileUtils:
    """测试文件工具类"""

    def test_get_upload_dir(self):
        """测试获取上传目录"""
        upload_dir = FileUtils.get_upload_dir()
        assert upload_dir == "static/uploads/damage_images"
        # 验证目录是否创建
        assert os.path.exists(upload_dir)

    def test_generate_filename_with_extension(self):
        """测试生成带扩展名的文件名"""
        original_filename = "test_image.jpg"
        generated_filename = FileUtils.generate_filename(original_filename)

        # 检查文件名格式: UUID + 扩展名
        assert generated_filename.endswith(".jpg")
        assert len(generated_filename) > 10  # UUID长度 + 扩展名

    def test_generate_filename_with_png_extension(self):
        """测试生成PNG扩展名的文件名"""
        original_filename = "photo.png"
        generated_filename = FileUtils.generate_filename(original_filename)

        assert generated_filename.endswith(".png")
        assert len(generated_filename) > 10

    def test_generate_filename_without_extension(self):
        """测试无扩展名的文件名生成"""
        original_filename = "noextension"
        generated_filename = FileUtils.generate_filename(original_filename)

        # 没有扩展名时，生成的文件名只有UUID部分
        assert "." not in generated_filename or generated_filename == generated_filename.rstrip(".")
        assert len(generated_filename) >= 36  # UUID标准长度

    def test_generate_filename_uniqueness(self):
        """测试文件名唯一性"""
        original_filename = "test.jpg"
        filename1 = FileUtils.generate_filename(original_filename)
        filename2 = FileUtils.generate_filename(original_filename)

        # 两次生成的文件名应该不同（UUID保证唯一性）
        assert filename1 != filename2
        assert filename1.endswith(".jpg")
        assert filename2.endswith(".jpg")

    @pytest.mark.asyncio
    async def test_save_upload_file_success(self, tmp_path):
        """测试成功保存上传文件"""
        # 创建Mock的UploadFile
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"test file content")
        mock_file.filename = "test.jpg"

        # 使用临时目录
        test_dir = str(tmp_path)
        test_filename = "test_file.jpg"

        # 保存文件
        result = await FileUtils.save_upload_file(mock_file, test_dir, test_filename)

        # 验证返回路径
        expected_path = os.path.join(test_dir, test_filename)
        assert result == expected_path

        # 验证文件已创建
        assert os.path.exists(result)

        # 验证文件内容
        with open(result, "rb") as f:
            content = f.read()
            assert content == b"test file content"

    @pytest.mark.asyncio
    async def test_save_damage_image_success(self, tmp_path):
        """测试成功保存病害图片"""
        # 创建Mock的UploadFile
        mock_image = AsyncMock()
        mock_image.filename = "damage.jpg"
        mock_image.content_type = "image/jpeg"
        # 模拟图片内容（小于5MB）
        mock_image.read = AsyncMock(return_value=b"fake image content" * 1000)

        # Mock get_upload_dir 返回临时目录
        with patch.object(FileUtils, "get_upload_dir", return_value=str(tmp_path)):
            result = await FileUtils.save_damage_image(mock_image)

        # 验证返回值格式
        assert result is not None
        assert result.startswith("damage_images/")
        assert result.endswith(".jpg")

        # 验证文件已创建
        file_name = result.split("/")[-1]
        file_path = os.path.join(str(tmp_path), file_name)
        assert os.path.exists(file_path)

    @pytest.mark.asyncio
    async def test_save_damage_image_no_file(self):
        """测试保存空文件"""
        result = await FileUtils.save_damage_image(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_save_damage_image_invalid_type(self):
        """测试不支持的图片格式"""
        mock_image = AsyncMock()
        mock_image.filename = "document.pdf"
        mock_image.content_type = "application/pdf"

        with pytest.raises(ValueError, match="不支持的图片格式"):
            await FileUtils.save_damage_image(mock_image)

    @pytest.mark.asyncio
    async def test_save_damage_image_size_exceeds_limit(self):
        """测试文件大小超过限制"""
        mock_image = AsyncMock()
        mock_image.filename = "large_image.jpg"
        mock_image.content_type = "image/jpeg"
        # 模拟大于5MB的图片
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        mock_image.read = AsyncMock(return_value=large_content)

        with pytest.raises(ValueError, match="图片文件大小不能超过5MB"):
            await FileUtils.save_damage_image(mock_image)

    @pytest.mark.asyncio
    async def test_save_damage_image_png_format(self, tmp_path):
        """测试保存PNG格式图片"""
        mock_image = AsyncMock()
        mock_image.filename = "photo.png"
        mock_image.content_type = "image/png"
        mock_image.read = AsyncMock(return_value=b"png image content")

        with patch.object(FileUtils, "get_upload_dir", return_value=str(tmp_path)):
            result = await FileUtils.save_damage_image(mock_image)

        assert result is not None
        assert result.endswith(".png")

    @pytest.mark.asyncio
    async def test_save_damage_image_jpg_format(self, tmp_path):
        """测试保存JPG格式图片（区别于JPEG）"""
        mock_image = AsyncMock()
        mock_image.filename = "photo.jpg"
        mock_image.content_type = "image/jpg"
        mock_image.read = AsyncMock(return_value=b"jpg image content")

        with patch.object(FileUtils, "get_upload_dir", return_value=str(tmp_path)):
            result = await FileUtils.save_damage_image(mock_image)

        assert result is not None
        assert result.endswith(".jpg")

    @pytest.mark.asyncio
    async def test_save_damage_image_read_error(self):
        """测试读取文件时发生错误"""
        mock_image = AsyncMock()
        mock_image.filename = "error.jpg"
        mock_image.content_type = "image/jpeg"
        # 模拟读取错误
        mock_image.read = AsyncMock(side_effect=Exception("Read error"))

        with pytest.raises(Exception, match="Read error"):
            await FileUtils.save_damage_image(mock_image)

    @pytest.mark.asyncio
    async def test_save_upload_file_write_error(self, tmp_path):
        """测试写入文件时发生错误"""
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"content")
        mock_file.filename = "test.jpg"

        # 使用不存在的目录路径来触发写入错误
        invalid_dir = "/invalid/nonexistent/directory"
        test_filename = "test.jpg"

        with pytest.raises(Exception):
            await FileUtils.save_upload_file(mock_file, invalid_dir, test_filename)
