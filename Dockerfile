FROM python:3.8

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "web_scraper_web.py"]


