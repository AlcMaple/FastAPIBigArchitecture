import os
import sys
import subprocess

def run_alembic(args):
    """通过 Python 执行 Alembic，剔除本地 alembic 目录以免发生包名冲突"""
    py_code = (
        "import sys, os; "
        "sys.path = [p for p in sys.path if p and os.path.abspath(p) != os.path.abspath(os.getcwd())]; "
        "from alembic.config import main; "
        "sys.exit(main())"
    )
    cmd = [sys.executable, "-c", py_code] + args
    subprocess.run(cmd, check=True)

def create_db_if_not_exists():
    from config.settings import settings
    from sqlalchemy.engine import make_url
    import pymysql

    url = make_url(settings.database_url)
    if url.get_backend_name() == 'mysql':
        try:
            conn = pymysql.connect(
                host=url.host,
                port=url.port or 3306,
                user=url.username,
                password=url.password
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{url.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"✅ 成功检查并确保数据库 `{url.database}` 存在。")
        except Exception as e:
            print(f"❌ 自动创建数据库失败，请检查数据库服务或配置：{e}")
            sys.exit(1)

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.chdir(project_root)
    
    print("🚀 开始初始化数据库...")
    
    # 尝试创建物理数据库
    create_db_if_not_exists()
    
    versions_dir = os.path.join(project_root, "alembic", "versions")
    has_migrations = False
    if os.path.isdir(versions_dir):
        if any(f.endswith('.py') for f in os.listdir(versions_dir)):
            has_migrations = True

    if not has_migrations:
        print("📁 未发现历史版本，正在生成初始版本...")
        try:
            run_alembic(["revision", "--autogenerate", "-m", "init database"])
        except subprocess.CalledProcessError as e:
            print(f"❌ 生成初始版本失败: {e}")
            sys.exit(1)
    else:
        print("📦 发现历史版本，跳过初始版本生成(如果是第一次拉取代码，将直接应用现有版本)...")
        
    print("🔄 正在应用数据表...")
    try:
        run_alembic(["upgrade", "head"])
        print("✅ 数据库初始化/更新完成！")
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库更新失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
