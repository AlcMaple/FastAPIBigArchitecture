"""
单元测试 - 日期时间工具函数

utils/datetime.py
"""

import pytest
from datetime import datetime, date, timedelta

from utils.datetime import diff_days_for_now_time


class TestDiffDaysForNowTime:
    """测试日期差值计算函数"""

    def test_future_date_datetime(self):
        """测试未来日期（datetime对象）"""
        # 未来3天
        future_date = datetime.now() + timedelta(days=3)
        assert diff_days_for_now_time(future_date) == 3

    def test_future_date_date(self):
        """测试未来日期（date对象）"""
        # 未来7天
        future_date = date.today() + timedelta(days=7)
        assert diff_days_for_now_time(future_date) == 7

    def test_past_date_datetime(self):
        """测试过去日期（datetime对象）"""
        # 过去5天
        past_date = datetime.now() - timedelta(days=5)
        assert diff_days_for_now_time(past_date) == -5

    def test_past_date_date(self):
        """测试过去日期（date对象）"""
        # 过去10天
        past_date = date.today() - timedelta(days=10)
        assert diff_days_for_now_time(past_date) == -10

    def test_today_datetime(self):
        """测试当天日期（datetime对象）"""
        # 今天（使用当前时间）
        today = datetime.now()
        assert diff_days_for_now_time(today) == 0

    def test_today_date(self):
        """测试当天日期（date对象）"""
        # 今天（使用date对象）
        today = date.today()
        assert diff_days_for_now_time(today) == 0

    def test_datetime_with_different_time(self):
        """测试同一天但不同时间的datetime对象"""
        # 同一天的凌晨和晚上应该都返回0
        morning = datetime.now().replace(hour=0, minute=0, second=0)
        evening = datetime.now().replace(hour=23, minute=59, second=59)

        assert diff_days_for_now_time(morning) == 0
        assert diff_days_for_now_time(evening) == 0

    def test_invalid_input_string(self):
        """测试无效输入 - 字符串"""
        with pytest.raises(ValueError, match="必须是 datetime 或 date 对象"):
            diff_days_for_now_time("2024-01-01")

    def test_invalid_input_int(self):
        """测试无效输入 - 整数"""
        with pytest.raises(ValueError, match="必须是 datetime 或 date 对象"):
            diff_days_for_now_time(123456)

    def test_invalid_input_none(self):
        """测试无效输入 - None"""
        with pytest.raises(ValueError, match="必须是 datetime 或 date 对象"):
            diff_days_for_now_time(None)

    def test_edge_case_30_days(self):
        """测试边界情况 - 30天后"""
        future_30_days = date.today() + timedelta(days=30)
        assert diff_days_for_now_time(future_30_days) == 30

    def test_edge_case_365_days(self):
        """测试边界情况 - 一年后"""
        future_1_year = date.today() + timedelta(days=365)
        assert diff_days_for_now_time(future_1_year) == 365
