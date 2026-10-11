# QA 테스트 실행 이미지: UI(Playwright)와 API(httpx) pytest를 한 이미지에서 돌린다.
# 이미지는 실행 환경(브라우저, 파이썬 패키지)만 고정한다. 코드와 결과는 폴더를 마운트해서 쓰므로
# 테스트를 고쳐도 다시 빌드하지 않는다. 계정 값(.env)은 이미지에 넣지 않고 마운트한 폴더에서 읽는다.
#   빌드(의존성이 바뀔 때만):  docker build -t qa-tests .
#   UI:   docker run --rm -v "$PWD/playwright-demo:/qa/playwright-demo" -w /qa/playwright-demo qa-tests pytest -m "not spec_undefined"
#   API:  docker run --rm -v "$PWD/api-demo:/qa/api-demo" -w /qa/api-demo qa-tests pytest -m "not spec_undefined"
#   결과: 각 폴더의 test-results/ (맥에서 바로 보인다)

FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

WORKDIR /qa

# 의존성 먼저 설치해 코드만 바뀌면 이 층을 재사용한다
COPY requirements.txt /tmp/req-ui.txt
COPY api-demo/requirements.txt /tmp/req-api.txt
# 이미지에 venv 모듈이 없고 컨테이너 하나가 환경 하나라서 시스템 Python에 바로 설치한다
RUN pip install --no-cache-dir --break-system-packages -r /tmp/req-ui.txt -r /tmp/req-api.txt
ENV PYTHONDONTWRITEBYTECODE=1

COPY playwright-demo/ playwright-demo/
COPY api-demo/ api-demo/
COPY scripts/ scripts/
