#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Custom AST-TTS 启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主启动函数"""
    print("🚀 Smart Custom AST-TTS 项目启动")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查关键文件
    print("📋 检查项目文件...")
    
    checks = [
        ("requirements.txt", "依赖配置"),
        (".env", "环境配置"),
        ("main.py", "主程序"),
        ("frontend/index.html", "前端页面"),
        ("backend/app/modules/ast_tts/controller.py", "控制器"),
    ]
    
    all_good = True
    for file_path, description in checks:
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} 不存在")
            all_good = False
    
    if not all_good:
        print("\n⚠️  警告: 部分文件缺失，项目可能无法正常运行")
        input("按回车键继续...")
    
    # 启动应用
    print("\n🚀 启动服务...")
    print("📖 访问地址:")
    print("   前端界面: http://localhost:8000")
    print("   API文档:  http://localhost:8000/docs")
    print("   健康检查: http://localhost:8000/api/ast-tts/health")
    print("\n" + "=" * 50)
    
    try:
        # 使用Python直接启动
        exec(open("main.py").read())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()