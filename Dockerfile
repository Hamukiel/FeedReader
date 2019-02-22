FROM python:3.6

WORKDIR /app

ADD ./src ./src
ADD requirements.txt ./
ADD run.sh ./

EXPOSE 5000

RUN pip install -r requirements.txt
RUN chmod +x ./run.sh
CMD ["./run.sh"]