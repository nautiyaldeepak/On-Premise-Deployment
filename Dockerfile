FROM python:3.6.5-slim
WORKDIR /app
ADD . /app
RUN pip install --trusted-host --no-cache flask ptvsd
EXPOSE 3000
CMD ["python", "app.py"]