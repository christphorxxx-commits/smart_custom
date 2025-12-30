#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目启动测试脚本
"""

import sys
import os
from pathlib import Path

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    # 添加backend路径
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    try:
        from app.modules.ast_tts.controller import ASTTTSRouter
        print("✅ AST-TTS模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_env_config():
    """测试环境配置"""
    print("🔍 测试环境配置...")
    
    # 检查.env文件
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env文件存在")
        
        # 检查API密钥
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DASHSCOPE_API_KEY' in content:
                print("✅ DASHSCOPE_API_KEY配置存在")
            else:
                print("⚠️  警告: DASHSCOPE_API_KEY未配置")
    else:
        print("⚠️  警告: .env文件不存在")
    
    return True

def test_requirements():
    """测试依赖"""
    print("🔍 测试依赖安装...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        print("✅ requirements.txt文件存在")
    else:
        print("❌ requirements.txt文件不存在")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始项目启动测试")
    print("=" * 50)
    
    # 执行测试
    tests = [
        test_requirements,
        test_env_config,
        test_imports,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试执行错误: {e}")
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{len(tests)} 项通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！项目可以正常启动")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()