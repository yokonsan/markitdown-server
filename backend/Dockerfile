FROM python:3.10-slim-bookworm AS builder

WORKDIR /opt/app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc-dev libffi-dev libssl-dev python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建并安装虚拟环境
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.10-slim-bookworm AS production

ENV TZ=UTC

WORKDIR /opt/app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 设置提交SHA
ARG COMMIT_SHA
ENV COMMIT_SHA=${COMMIT_SHA}

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]