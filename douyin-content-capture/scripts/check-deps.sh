#!/usr/bin/env bash
# ============================================================
# 抖音内容提取 - 依赖检查与安装脚本
# 检查并安装所有必需的系统和 Python 依赖
# ============================================================
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="${SKILL_DIR}/obsidian-content-capture-backend"
VENV_DIR="${PROJECT_DIR}/.venv"
ENV_FILE="${SKILL_DIR}/.env"
ENV_EXAMPLE="${SKILL_DIR}/.env.example"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }

ERRORS=()

echo ""
echo "=========================================="
echo "  抖音内容提取 - 依赖检查"
echo "=========================================="
echo ""

# -----------------------------------------------------------
# 1. 检查 Python 3.10+
# -----------------------------------------------------------
info "检查 Python 版本..."
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0")
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -ge 3 ]] && [[ "$minor" -ge 10 ]]; then
            PYTHON_CMD="$cmd"
            ok "Python $version ($cmd)"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    fail "未找到 Python 3.10+"
    ERRORS+=("Python 3.10+ 未安装。macOS: brew install python@3.12")
fi

# -----------------------------------------------------------
# 2. 检查 FFmpeg
# -----------------------------------------------------------
info "检查 FFmpeg..."
if command -v ffmpeg &>/dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -1)
    ok "FFmpeg 已安装: ${ffmpeg_version}"
else
    fail "FFmpeg 未安装"
    ERRORS+=("FFmpeg 未安装。macOS: brew install ffmpeg / Ubuntu: sudo apt install ffmpeg")
fi

# -----------------------------------------------------------
# 3. 检查/克隆项目源码
# -----------------------------------------------------------
# 源码仓库地址（可通过环境变量 DOUYIN_REPO_URL 自定义）
REPO_URL="${DOUYIN_REPO_URL:-https://github.com/zhaoyaoyuan/obsidian-content-capture-backend.git}"

info "检查项目源码..."
if [[ -d "${PROJECT_DIR}/script" ]]; then
    ok "项目源码已存在: ${PROJECT_DIR}"
else
    info "正在克隆项目源码..."
    info "仓库地址: ${REPO_URL}"
    if command -v git &>/dev/null; then
        git clone "${REPO_URL}" "${PROJECT_DIR}" 2>&1
        ok "项目源码克隆完成"
    else
        fail "Git 未安装，无法克隆项目"
        ERRORS+=("Git 未安装。macOS: brew install git")
    fi
fi

# -----------------------------------------------------------
# 4. 创建 venv 并安装 Python 依赖
# -----------------------------------------------------------
if [[ -n "$PYTHON_CMD" ]] && [[ -d "${PROJECT_DIR}/script" ]]; then
    info "检查 Python 虚拟环境..."

    if [[ ! -d "${VENV_DIR}" ]]; then
        info "创建虚拟环境: ${VENV_DIR}"
        "$PYTHON_CMD" -m venv "${VENV_DIR}"
        ok "虚拟环境创建完成"
    else
        ok "虚拟环境已存在"
    fi

    info "检查/安装 Python 依赖..."
    VENV_PIP="${VENV_DIR}/bin/pip"

    # 检查关键包是否已安装
    NEED_INSTALL=false
    for pkg in requests faster_whisper zhconv; do
        if ! "${VENV_DIR}/bin/python" -c "import ${pkg}" 2>/dev/null; then
            NEED_INSTALL=true
            break
        fi
    done

    if [[ "$NEED_INSTALL" == "true" ]]; then
        info "安装 Python 依赖（可能需要几分钟）..."
        "${VENV_PIP}" install --upgrade pip -q
        "${VENV_PIP}" install -r "${PROJECT_DIR}/requirements.txt" -q
        ok "Python 依赖安装完成"
    else
        ok "Python 依赖已就绪"
    fi
fi

# -----------------------------------------------------------
# 5. 检查/创建 .env 配置
# -----------------------------------------------------------
info "检查环境配置..."
if [[ -f "${ENV_FILE}" ]]; then
    ok ".env 配置文件已存在"
    
    # 检查是否配置了输出目录
    OUTPUT_DIR=$(grep -E '^DOUYIN_OUTPUT_DIR=' "${ENV_FILE}" | cut -d= -f2- | sed 's/#.*//' | xargs 2>/dev/null || echo "")
    if [[ -z "$OUTPUT_DIR" ]]; then
        warn "未配置 DOUYIN_OUTPUT_DIR，请编辑: ${ENV_FILE}"
    else
        ok "输出目录: ${OUTPUT_DIR}"
    fi
else
    if [[ -f "${ENV_EXAMPLE}" ]]; then
        cp "${ENV_EXAMPLE}" "${ENV_FILE}"
        ok "已从 .env.example 创建 .env 配置文件"
    else
        # 创建配置文件（不含默认目录）
        cat > "${ENV_FILE}" << 'EOF'
# 抖音内容提取 - 环境配置
# 请修改下面的路径为你想要的下载输出目录

# DOUYIN_OUTPUT_DIR=~/Downloads/douyin-captures
DOUYIN_WHISPER_MODEL=small
DOUYIN_WHISPER_DEVICE=auto
EOF
        ok "已创建 .env 配置文件"
    fi
    
    echo ""
    warn "⚠️  请编辑配置文件设置输出目录:"
    echo "    ${ENV_FILE}"
    echo ""
    echo "    取消注释并修改 DOUYIN_OUTPUT_DIR 为你想要的目录，例如:"
    echo "    DOUYIN_OUTPUT_DIR=~/Downloads/my-douyin"
    echo ""
fi

# -----------------------------------------------------------
# 总结
# -----------------------------------------------------------
echo ""
echo "=========================================="
if [[ ${#ERRORS[@]} -eq 0 ]]; then
    echo -e "  ${GREEN}✓ 所有依赖检查通过${NC}"
    echo "=========================================="
    echo ""
    echo "使用方式:"
    echo "  bash ${SKILL_DIR}/scripts/run.sh \"抖音分享链接\""
    echo ""
    exit 0
else
    echo -e "  ${RED}✗ 发现 ${#ERRORS[@]} 个问题${NC}"
    echo "=========================================="
    echo ""
    for err in "${ERRORS[@]}"; do
        echo -e "  ${RED}•${NC} ${err}"
    done
    echo ""
    exit 1
fi
