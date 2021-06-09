FROM ubuntu:16.04

RUN apt-get update -y && \
    apt install -y python3-pip python3 && \
    apt-get -y install locales && \
    apt-get -y install jq

RUN apt-get install -y ngrok-client
RUN apt-get install -y curl

# Set the locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8     

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r ./requirements.txt


COPY . /app

RUN ngrok http 5000 &

RUN export WEBHOOK_URL="$(curl http://localhost:4040/api/tunnels | jq ".tunnels[0].public_url")"

RUN echo 'PAPICH_NGROK_URL="$WEBHOOK_URL"' >> .env

RUN cat .env

RUN python3 papich_media_server/manage.py flush
RUN python3 papich_media_server/manage.py loaddata papich_media_server/seeds.json

RUN python3 papich_media_server/manage.py runserver

ENTRYPOINT [ "python3" ]

CMD [ "server.py" ]
