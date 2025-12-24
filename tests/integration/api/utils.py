# tests/integration/api/utils.py
from httpx import Response
from typing import Any, Dict, Optional, Union

from exts.exceptions.error_code import ErrorCode


def assert_api_success(
    response: Response, expected_http_status: int = 200
) -> Dict[str, Any]:
    """
    验证 API 调用成功

    Args:
        response: 接口响应对象
        expected_http_status: 预期的 HTTP 状态码 (默认 200)

    Returns:
        Dict: 响应中的 data 数据
    """
    # 验证 HTTP 状态码
    assert response.status_code == expected_http_status, (
        f"HTTP状态码错误: 预期 {expected_http_status}, "
        f"实际 {response.status_code}, 响应: {response.text}"
    )

    data = response.json()

    # 验证业务状态码
    assert (
        data["code"] == ErrorCode.SUCCESS.code
    ), f"业务Code错误: 预期 {ErrorCode.SUCCESS.code}, 实际 {data.get('code')}"

    # 返回 data 供后续校验具体字段
    return data.get("data", {})


def assert_api_failure(
    response: Response,
    expected_error: ErrorCode,
    match_msg: str = "",
):
    """
    验证 API 调用失败

    Args:
        response: 接口响应对象
        expected_error: 预期的错误类型 (ErrorCode 枚举)
        match_msg: 错误信息中必须包含的关键词
    """
    data = response.json()
    assert response.status_code == expected_error.http_status, (
        f"HTTP状态码不匹配: 预期 {expected_error.http_status} ({expected_error.name}), "
        f"实际 {response.status_code}. 响应体: {data}"
    )

    # 验证业务错误码
    assert data["code"] == expected_error.code, (
        f"业务错误码不匹配: 预期 {expected_error.code}, " f"实际 {data.get('code')}"
    )

    # 验证 success 字段
    if "success" in data:
        assert data["success"] is False, "预期失败，实际却标记为成功"

    # 验证错误信息包含特定关键词
    if match_msg:
        actual_msg = data.get("message", "")
        actual_detail = str(data.get("data", {}))
        assert match_msg in actual_msg or match_msg in actual_detail, (
            f"错误信息未包含关键词 '{match_msg}'. "
            f"实际 Message: '{actual_msg}', Detail: '{actual_detail}'"
        )
