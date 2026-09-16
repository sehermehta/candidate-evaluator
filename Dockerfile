FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY candidate_evaluator/ ./candidate_evaluator/
COPY rubrics/ ./rubrics/
COPY .streamlit/config.toml ./.streamlit/config.toml
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "exec streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false"]
