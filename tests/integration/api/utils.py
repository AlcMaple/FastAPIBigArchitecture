# tests/integration/api/utils.py
from httpx import Response
from typing import Any, Dict, Optional


def assert_api_success(response: Response) -> Dict[str, Any]:
    """
    通用断言：验证 API 调用成功
    1. HTTP 状态码必须是 200
    2. JSON 里的 success 必须是 True
    3. 返回 data 字段供进一步校验
    """
    assert response.status_code == 200, f"HTTP 状态码错误: {response.text}"

    data = response.json()
    assert data["success"] is True, f"业务逻辑失败: {data.get('message')}"
    assert data["code"] == 200
    return data["data"]


def assert_api_failure(
    response: Response,
    expected_code: Optional[int] = None,
    match_msg: str = "",
    status_code: int = 200,
):
    """
    通用断言：验证 API 调用失败
    1. 验证 HTTP 状态码 (业务错误通常是 200，Pydantic 校验通常是 422)
    2. 验证 success 是 False
    3. 验证错误码 (可选)
    4. 验证错误信息包含特定关键词
    """
    assert (
        response.status_code == status_code
    ), f"预期 HTTP {status_code}, 实际 {response.status_code}"

    data = response.json()
    assert data["success"] is False, "预期失败，实际却成功了"

    if expected_code:
        assert (
            data["code"] == expected_code
        ), f"预期错误码 {expected_code}, 实际 {data['code']}"

    if match_msg:
        assert (
            match_msg in data["message"]
        ), f"错误信息 '{data['message']}' 未包含 '{match_msg}'"
