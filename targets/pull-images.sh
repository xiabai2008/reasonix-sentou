#!/bin/bash
# Reasonix 靶场 — 镜像拉取脚本 (通过 1ms.run 镜像加速)
# 用法: bash targets/pull-images.sh

MIRROR="docker.1ms.run"
echo "=== Reasonix 靶场镜像拉取 ==="
echo "镜像源: $MIRROR"
echo ""

pull_and_tag() {
    local image="$1"
    local mirror_image="$MIRROR/$image"
    echo "[*] $mirror_image ..."
    docker pull "$mirror_image" 2>&1 | grep -E "(Pulled|Downloaded|Already|exists)"
    docker tag "$mirror_image" "$image" 2>/dev/null
    echo "    OK: $image"
    echo ""
}

# 核心靶场
pull_and_tag "vulnerables/web-dvwa:latest"
pull_and_tag "library/mysql:5.7"
pull_and_tag "bkimminich/juice-shop:latest"
pull_and_tag "webgoat/goatandwolf:latest"
pull_and_tag "erev0s/vampi:latest"

echo "=== 镜像拉取完成 ==="
echo "运行: cd targets && docker compose up -d"
