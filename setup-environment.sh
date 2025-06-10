#!/bin/bash

# Elodin 项目环境设置脚本
# 此脚本将安装运行 Elodin 项目所需的所有依赖

set -e

echo "🚀 开始设置 Elodin 开发环境..."

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "📋 检测到操作系统: $OS"

# 安装系统依赖
install_system_deps() {
    echo "📦 安装系统依赖..."
    
    if [[ "$OS" == "linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                build-essential \
                pkg-config \
                libssl-dev \
                libasound2-dev \
                libxkbcommon-dev \
                libwayland-dev \
                libgtk-3-dev \
                libudev-dev \
                libfontconfig1-dev \
                cmake \
                python3 \
                python3-pip \
                python3-venv \
                gfortran \
                libgfortran5 \
                ffmpeg \
                libgstreamer1.0-dev \
                libgstreamer-plugins-base1.0-dev \
                libgstreamer-plugins-good1.0-dev
        # CentOS/RHEL/Fedora
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y \
                curl \
                gcc \
                gcc-c++ \
                pkg-config \
                openssl-devel \
                alsa-lib-devel \
                libxkbcommon-devel \
                wayland-devel \
                gtk3-devel \
                systemd-devel \
                fontconfig-devel \
                cmake \
                python3 \
                python3-pip \
                gfortran \
                ffmpeg-devel \
                gstreamer1-devel \
                gstreamer1-plugins-base-devel
        fi
    elif [[ "$OS" == "macos" ]]; then
        # macOS - 使用 Homebrew
        if ! command -v brew &> /dev/null; then
            echo "🍺 安装 Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        brew install \
            cmake \
            pkg-config \
            python3 \
            gfortran \
            ffmpeg \
            gstreamer \
            gtk+3
    fi
}

# 安装 Rust
install_rust() {
    if ! command -v cargo &> /dev/null; then
        echo "🦀 安装 Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
        
        # 添加必要的目标平台
        rustup target add wasm32-unknown-unknown
        rustup target add thumbv7em-none-eabihf
    else
        echo "✅ Rust 已安装"
    fi
}

# 安装 Python 依赖管理工具
install_python_tools() {
    echo "🐍 安装 Python 工具..."
    
    # 安装 uv (现代 Python 包管理器)
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.local/bin/env
    fi
    
    # 安装 maturin (Python-Rust 绑定构建工具)
    if ! command -v maturin &> /dev/null; then
        pip3 install --user maturin
    fi
}

# 安装 Nix (可选，用于完整的开发环境)
install_nix() {
    if ! command -v nix &> /dev/null; then
        echo "❄️  安装 Nix (可选)..."
        read -p "是否安装 Nix? 这将提供完整的开发环境 (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
            source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
        fi
    else
        echo "✅ Nix 已安装"
    fi
}

# 构建项目
build_project() {
    echo "🔨 构建项目..."
    
    # 构建 Rust 组件
    echo "构建 Rust 组件..."
    cargo build --release --package elodin --package elodin-db
    
    # 构建 Python 组件
    echo "构建 Python 组件..."
    cd libs/nox-py
    
    # 创建虚拟环境
    if [[ ! -d ".venv" ]]; then
        uv venv
    fi
    
    # 激活虚拟环境并构建
    source .venv/bin/activate
    uv pip install maturin
    maturin develop --uv
    
    cd ../..
    
    echo "✅ 构建完成!"
}

# 运行测试
run_tests() {
    echo "🧪 运行测试..."
    
    # 运行 Rust 测试
    cargo test --workspace
    
    # 运行 Python 测试
    cd libs/nox-py
    source .venv/bin/activate
    python -m pytest
    cd ../..
    
    echo "✅ 测试完成!"
}

# 主函数
main() {
    install_system_deps
    install_rust
    install_python_tools
    install_nix
    
    echo "🎯 环境设置完成!"
    echo ""
    echo "下一步:"
    echo "1. 重新加载 shell 环境: source ~/.bashrc (或重启终端)"
    echo "2. 构建项目: ./setup-environment.sh build"
    echo "3. 运行示例: elodin editor libs/nox-py/examples/three-body.py"
    echo ""
    echo "或者使用预编译版本:"
    echo "curl -LsSf https://storage.googleapis.com/elodin-releases/install-editor.sh | sh"
}

# 处理命令行参数
case "${1:-}" in
    "build")
        build_project
        ;;
    "test")
        run_tests
        ;;
    *)
        main
        ;;
esac
