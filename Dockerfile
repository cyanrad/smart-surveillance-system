FROM nvcr.io/nvidia/pytorch:23.04-py3
WORKDIR /code
COPY requirements.txt ./
RUN pip install -r /code/requirements.txt
COPY . .
EXPOSE 8000
ENV HOST 'host.docker.internal'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]