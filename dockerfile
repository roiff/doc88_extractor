# 多阶段构建 Dockerfile

# 第一阶段: 基础镜像,包含Python和Java

FROM python:3.11-slim as base

# 设置工作目录
COPY . /app
WORKDIR /app

RUN echo 'APT::Update::Post-Invoke-Success {"touch /var/lib/apt/periodic/update-success-stamp 2>/dev/null || true";};' > /etc/apt/apt.conf.d/00_disable-success-stamp


# 安装系统依赖、Java和中文字体
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    openjdk-17-jdk \
    libcairo2 \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    shared-mime-info \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-microhei \
    fonts-wqy-zenhei && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/archives/*.deb

# 设置Java环境变量

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=”${JAVA_HOME}/bin:${PATH}”

# 第二阶段: 安装Python依赖

FROM base as dependencies


# 升级pip并安装Python依赖

RUN pip install –no-cache-dir –upgrade pip &&   \
pip install –no-cache-dir -r requirements.txt &&   \
pip install –no-cache-dir cairosvg

# 第三阶段: 最终镜像

FROM dependencies as final


# 设置环境变量

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8

# 验证中文字体安装
RUN fc-list :lang=zh

# 默认命令

CMD [“python”, app.py”]
