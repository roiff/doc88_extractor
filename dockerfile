# 多阶段构建 Dockerfile

# 第一阶段: 基础镜像,包含Python和Java

FROM python:3.11

# 设置工作目录
COPY . /app
WORKDIR /app

# 安装系统依赖、Java和中文字体
RUN apt-get update || true && \
    openjdk-17-jdk \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-microhei \
    fonts-wqy-zenhei && \
    fc-cache -fv && \
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
