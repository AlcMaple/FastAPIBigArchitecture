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

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    print("🚧 数据库自动迁移工具 🚧")
    message = input("请输入本次表结构更新的说明（例如 'add article table'）: ").strip()
    
    if not message:
        print("❌ 错误：更新说明不能为空！")
        sys.exit(1)
        
    print(f"📁 正在生成新版本 [ {message} ] ...")
    try:
        run_alembic(["revision", "--autogenerate", "-m", message])
    except subprocess.CalledProcessError as e:
        print(f"❌ 生成迁移版本失败: {e}")
        sys.exit(1)

    print("")
    print("⚠️  请打开 alembic/versions/ 下最新生成的脚本进行人工检查：")
    print("   - 列改名是否被误识别为 drop_column + add_column")
    print("   - 类型变更是否带上 existing_type / existing_nullable")
    print("   - 收窄类型 / 删列 前是否需要补数据清洗或备份 SQL")
    print("   - downgrade() 是否写对，能否回滚")
    print("")
    confirm = input("检查/修改完成后输入 y 继续应用到数据库，其它任意键取消: ").strip().lower()
    if confirm != "y":
        print("🛑 已取消 upgrade。生成的脚本保留在 alembic/versions/，可手动编辑后再运行 `alembic upgrade head`。")
        sys.exit(0)

    print("🔄 正在应用更新到数据库...")
    try:
        run_alembic(["upgrade", "head"])
        print("✅ 数据库更新并应用完成！")
    except subprocess.CalledProcessError as e:
        print(f"❌ 应用版本到数据库失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
