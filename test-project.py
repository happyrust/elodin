#!/usr/bin/env python3
"""
Elodin 项目测试脚本
用于验证项目是否能正常运行
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"
    except Exception as e:
        return False, "", str(e)

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    checks = []
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        checks.append(("✅", f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"))
    else:
        checks.append(("❌", f"Python 版本过低: {python_version.major}.{python_version.minor}"))
    
    # 检查必要的命令
    commands = ["curl", "git", "cmake", "pkg-config"]
    for cmd in commands:
        success, _, _ = run_command(f"which {cmd}")
        if success:
            checks.append(("✅", f"{cmd} 已安装"))
        else:
            checks.append(("❌", f"{cmd} 未安装"))
    
    # 检查 Rust
    success, stdout, _ = run_command("rustc --version")
    if success:
        checks.append(("✅", f"Rust: {stdout.strip()}"))
    else:
        checks.append(("❌", "Rust 未安装"))
    
    # 检查 Cargo
    success, stdout, _ = run_command("cargo --version")
    if success:
        checks.append(("✅", f"Cargo: {stdout.strip()}"))
    else:
        checks.append(("❌", "Cargo 未安装"))
    
    for status, message in checks:
        print(f"  {status} {message}")
    
    return all(status == "✅" for status, _ in checks)

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = [
        "apps/elodin",
        "libs/nox-py", 
        "libs/nox",
        "libs/elodin-editor",
        "libs/db",
        "fsw",
        "examples"
    ]
    
    required_files = [
        "Cargo.toml",
        "rust-toolchain.toml",
        "flake.nix",
        "justfile"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ (缺失)")
            all_good = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
            all_good = False
    
    return all_good

def test_cargo_check():
    """测试 Cargo 检查"""
    print("\n🦀 运行 Cargo 检查...")
    
    success, stdout, stderr = run_command("cargo check --workspace")
    
    if success:
        print("  ✅ Cargo 检查通过")
        return True
    else:
        print("  ❌ Cargo 检查失败")
        print(f"  错误: {stderr}")
        return False

def test_python_imports():
    """测试 Python 导入"""
    print("\n🐍 测试 Python 导入...")
    
    # 检查基础 Python 包
    basic_packages = ["json", "pathlib", "subprocess", "sys", "os"]
    
    for package in basic_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (导入失败)")
            return False
    
    # 尝试导入 elodin (如果已构建)
    try:
        sys.path.insert(0, "libs/nox-py")
        import elodin
        print("  ✅ elodin (Python 绑定)")
        return True
    except ImportError:
        print("  ⚠️  elodin Python 绑定未构建 (这是正常的)")
        return True

def test_examples():
    """测试示例文件"""
    print("\n📝 检查示例文件...")
    
    example_files = [
        "libs/nox-py/examples/three-body.py",
        "libs/nox-py/examples/rocket.py", 
        "libs/nox-py/examples/cube-sat.py",
        "examples/drone/main.py",
        "examples/ball/main.py"
    ]
    
    all_good = True
    
    for example in example_files:
        if Path(example).exists():
            print(f"  ✅ {example}")
            
            # 简单语法检查
            try:
                with open(example, 'r') as f:
                    compile(f.read(), example, 'exec')
                print(f"    ✅ 语法检查通过")
            except SyntaxError as e:
                print(f"    ❌ 语法错误: {e}")
                all_good = False
        else:
            print(f"  ❌ {example} (缺失)")
            all_good = False
    
    return all_good

def generate_report():
    """生成测试报告"""
    print("\n📊 生成测试报告...")
    
    # 收集项目信息
    project_info = {}
    
    # Cargo 信息
    success, stdout, _ = run_command("cargo metadata --format-version 1")
    if success:
        try:
            metadata = json.loads(stdout)
            project_info["workspace_members"] = len(metadata.get("workspace_members", []))
            project_info["packages"] = len(metadata.get("packages", []))
        except:
            pass
    
    # Git 信息
    success, stdout, _ = run_command("git rev-parse --short HEAD")
    if success:
        project_info["git_commit"] = stdout.strip()
    
    success, stdout, _ = run_command("git branch --show-current")
    if success:
        project_info["git_branch"] = stdout.strip()
    
    # 文件统计
    rust_files = len(list(Path(".").rglob("*.rs")))
    python_files = len(list(Path(".").rglob("*.py")))
    
    project_info.update({
        "rust_files": rust_files,
        "python_files": python_files,
        "total_files": rust_files + python_files
    })
    
    print("项目统计:")
    for key, value in project_info.items():
        print(f"  {key}: {value}")
    
    return project_info

def main():
    """主函数"""
    print("🚀 Elodin 项目测试")
    print("=" * 50)
    
    # 检查当前目录是否是项目根目录
    if not Path("Cargo.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    tests = [
        ("系统要求", check_system_requirements),
        ("项目结构", check_project_structure), 
        ("Cargo 检查", test_cargo_check),
        ("Python 导入", test_python_imports),
        ("示例文件", test_examples)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ 测试 {test_name} 时出错: {e}")
            results.append((test_name, False))
    
    # 生成报告
    generate_report()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过! 项目状态良好。")
        print("\n下一步:")
        print("1. 运行 ./setup-environment.sh 安装依赖")
        print("2. 运行 ./setup-environment.sh build 构建项目")
        print("3. 运行示例: elodin editor libs/nox-py/examples/three-body.py")
    else:
        print(f"\n⚠️  有 {len(results) - passed} 项测试失败，请检查上述问题。")
        sys.exit(1)

if __name__ == "__main__":
    main()
