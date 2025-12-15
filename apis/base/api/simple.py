"""
特点
    - 请求参数少、响应结果少
    - 接口没有复杂的业务逻辑，标题即内容的接口
"""

from fastapi import Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.api_response import Success
