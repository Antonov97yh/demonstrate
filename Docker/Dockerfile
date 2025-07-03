FROM python:3.9-slim-buster

WORKDIR /sklonnost_klientov_k_produktam/source

COPY Docker/python_deps.txt .

RUN apt-get update
RUN apt-get install libgomp1
RUN pip install --no-cache-dir -r python_deps.txt

# COPY Site ./Site
# CMD ["python3", "Site/run.py"]
# something else?

CMD ["python3", "Site/run.py"]