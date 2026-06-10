#!/usr/bin/env bash
# ============================================================
# 抖音内容提取 - 主运行脚本
# 使用方法: bash run.sh [选项] "抖音分享链接"
# ============================================================
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="${SKILL_DIR}/obsidian-content-capture-backend"
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
ENV_FILE="${SKILL_DIR}/.env"

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

# -----------------------------------------------------------
# 预检查
# -----------------------------------------------------------

# 检查项目源码
if [[ ! -d "${PROJECT_DIR}/script" ]]; then
    fail "项目源码不存在，请先运行依赖检查:"
    echo "  bash ${SKILL_DIR}/scripts/check-deps.sh"
    exit 1
fi

# 检查 venv
if [[ ! -f "${VENV_PYTHON}" ]]; then
    fail "Python 虚拟环境不存在，请先运行依赖检查:"
    echo "  bash ${SKILL_DIR}/scripts/check-deps.sh"
    exit 1
fi

# -----------------------------------------------------------
# 加载 .env 配置
# -----------------------------------------------------------
load_env() {
    if [[ -f "${ENV_FILE}" ]]; then
        # 只读取非注释、非空行
        while IFS='=' read -r key value; do
            # 跳过注释和空行
            [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
            # 去除首尾空格
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | sed 's/#.*//' | xargs)
            # 导出变量
            export "$key=$value" 2>/dev/null || true
        done < "${ENV_FILE}"
    fi
}

load_env

# 检查并配置输出目录
check_output_dir() {
    # 如果 .env 不存在，尝试创建
    if [[ ! -f "${ENV_FILE}" ]]; then
        ENV_EXAMPLE="${SKILL_DIR}/.env.example"
        
        echo ""
        echo "============================================"
        echo "  ❌ 错误: 未找到配置文件"
        echo "============================================"
        echo ""
        echo "抖音内容提取需要配置输出目录才能正常运行。"
        echo ""
        
        if [[ -f "${ENV_EXAMPLE}" ]]; then
            echo "检测到 .env.example 模板，正在创建 .env 配置文件..."
            cp "${ENV_EXAMPLE}" "${ENV_FILE}"
            ok "已创建: ${ENV_FILE}"
        else
            echo "正在创建 .env 配置文件..."
            cat > "${ENV_FILE}" << 'ENVEOF'
# 抖音内容提取 - 环境配置
# 请修改下面的路径为你想要的下载输出目录

DOUYIN_OUTPUT_DIR=~/Downloads/douyin-captures
DOUYIN_WHISPER_MODEL=small
DOUYIN_WHISPER_DEVICE=auto
ENVEOF
            ok "已创建: ${ENV_FILE}"
        fi
        
        echo ""
        echo "📝 请按以下步骤配置:"
        echo "--------------------------------------------"
        echo "1. 编辑配置文件: ${ENV_FILE}"
        echo "2. 修改 DOUYIN_OUTPUT_DIR 为你的下载输出目录"
        echo "3. 重新运行此命令"
        echo "--------------------------------------------"
        echo ""
        echo "示例配置:"
        echo "  DOUYIN_OUTPUT_DIR=~/Downloads/my-douyin"
        echo ""
        exit 1
    fi
    
    # 检查是否配置了输出目录
    if [[ -z "${DOUYIN_OUTPUT_DIR:-}" ]]; then
        echo ""
        echo "============================================"
        echo "  ❌ 错误: 未配置输出目录"
        echo "============================================"
        echo ""
        echo "请在 ${ENV_FILE} 中配置 DOUYIN_OUTPUT_DIR"
        echo ""
        echo "示例:"
        echo "  DOUYIN_OUTPUT_DIR=~/Downloads/douyin-captures"
        echo ""
        exit 1
    fi
}

check_output_dir

# 读取配置
OUTPUT_DIR="${DOUYIN_OUTPUT_DIR}"
WHISPER_MODEL="${DOUYIN_WHISPER_MODEL:-small}"
WHISPER_DEVICE="${DOUYIN_WHISPER_DEVICE:-auto}"

# 展开 ~
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"

# -----------------------------------------------------------
# 解析命令行参数
# -----------------------------------------------------------
EXTRA_ARGS=()
CUSTOM_OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            CUSTOM_OUTPUT="$2"
            shift 2
            ;;
        --model)
            WHISPER_MODEL="$2"
            shift 2
            ;;
        --device)
            WHISPER_DEVICE="$2"
            shift 2
            ;;
        --compute-type)
            EXTRA_ARGS+=("--compute-type" "$2")
            shift 2
            ;;
        -h|--help)
            echo "抖音内容提取工具"
            echo ""
            echo "用法: bash run.sh [选项] \"抖音分享链接\""
            echo ""
            echo "选项:"
            echo "  -o, --output DIR     指定输出目录（默认: 从 .env 读取）"
            echo "  --model MODEL        Whisper 模型: tiny/base/small/medium/large-v2/large-v3"
            echo "  --device DEVICE      推理设备: auto/cpu/cuda"
            echo "  --compute-type TYPE  计算精度: int8/float16/default"
            echo ""
            echo "  -h, --help           显示帮助"
            echo ""
            echo "环境配置: ${ENV_FILE}"
            echo "默认输出: ${OUTPUT_DIR}"
            exit 0
            ;;
        *)
            # 其他参数作为 URL
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# 输出目录优先级: 命令行 > .env > 默认值
FINAL_OUTPUT="${CUSTOM_OUTPUT:-$OUTPUT_DIR}"
mkdir -p "${FINAL_OUTPUT}" 2>/dev/null || true

# -----------------------------------------------------------
# 运行
# -----------------------------------------------------------
info "配置信息:"
info "  输出目录: ${FINAL_OUTPUT}"
info "  Whisper 模型: ${WHISPER_MODEL}"
info "  推理设备: ${WHISPER_DEVICE}"
echo ""

# 构建完整参数
RUN_ARGS=(
    "-o" "${FINAL_OUTPUT}"
    "--model" "${WHISPER_MODEL}"
    "--device" "${WHISPER_DEVICE}"
)



# 添加额外参数和 URL
RUN_ARGS+=("${EXTRA_ARGS[@]}")

info "开始处理..."
echo ""

cd "${PROJECT_DIR}"
exec "${VENV_PYTHON}" -m script "${RUN_ARGS[@]}"
