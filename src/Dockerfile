FROM python:3.12-slim
LABEL authors="DEpishev@alfabank.ru"
ENV PYTHONUNBUFFERED=1
WORKDIR /home/parser
COPY parse-videoshopper.py /home/parser/parse-videoshopper.py
COPY requirements.txt /home/parser/requirements.txt
RUN pip install -r /home/parser/requirements.txt

ENTRYPOINT ["python3", "/home/parser/parse-videoshopper.py"]