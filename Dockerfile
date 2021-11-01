FROM python:3.9 AS builder
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m venv /opt/venv
COPY ./src /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM builder AS linting
RUN pip install --no-cache-dir --upgrade autopep8==1.5
COPY ./src /app
# Fail when autopep8 finds errors:
# https://es.stackoverflow.com/questions/487904/make-autopep8-fail-in-a-docker-build
RUN autopep8 -rd . && if [ -n "$(autopep8 -rd /app)" ]; then exit 1; fi

FROM python:3.9
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./src /app
RUN rm -rf /app/test
CMD ["python", "/app/main.py"]