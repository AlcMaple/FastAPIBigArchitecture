from datetime import datetime, date


def diff_days_for_now_time(target_date) -> int:
    """
    计算目标日期与当前时间的天数差
    
    :param target_date: 目标日期，可以是 datetime 或 date 对象
    :return: 天数差（正数表示未来，负数表示过去，0表示今天）
    """
    now = datetime.now()
    
    # 如果传入的是 datetime 对象，只取日期部分进行比较
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    elif isinstance(target_date, date):
        pass  # 已经是 date 对象，无需转换
    else:
        raise ValueError("target_date 必须是 datetime 或 date 对象")
    
    # 将当前时间也转换为日期进行比较
    current_date = now.date()
    
    # 计算天数差
    diff = (target_date - current_date).days
    
    return diff