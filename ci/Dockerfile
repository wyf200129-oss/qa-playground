# ── Jenkins CI 镜像：Python 3 + Chrome + Allure ──
FROM jenkins/jenkins:lts-jdk17

USER root

# 安装 Python3 / pip / venv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        wget gnupg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 设置 python/pip 别名
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    python -m pip install --upgrade pip

# 安装 Google Chrome（Selenium 依赖）
RUN wget -q -O /tmp/chrome.deb \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y --fix-broken /tmp/chrome.deb && \
    rm /tmp/chrome.deb && \
    rm -rf /var/lib/apt/lists/*

# 预装 Allure 命令行工具（用于生成报告）
RUN wget -q -O /tmp/allure.tgz \
        https://github.com/allure-framework/allure2/releases/download/2.30.0/allure-2.30.0.tgz && \
    tar -xzf /tmp/allure.tgz -C /opt && \
    ln -s /opt/allure-2.30.0/bin/allure /usr/local/bin/allure && \
    rm /tmp/allure.tgz

# 安装 Jenkins 插件
RUN jenkins-plugin-cli --plugins allure-jenkins-plugin:2.29.1

USER jenkins

# 设置默认 CI 环境变量（Chrome 无头模式）
ENV CI=true
ENV DISPLAY=:99
