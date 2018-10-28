FROM ubuntu:latest
RUN apt-get update && apt-get install -y software-properties-common ca-certificates curl
RUN gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4

RUN curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.4/gosu-$(dpkg --print-architecture)" \
    && curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.4/gosu-$(dpkg --print-architecture).asc" \
    && gpg --verify /usr/local/bin/gosu.asc \
    && rm /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu

COPY build/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

COPY build/bashrc /home/user/.bashrc
COPY build/bashrc /root/.bashrc
RUN echo "source .bashrc" > /home/user/.bash_profile
RUN echo "source .bashrc" > /root/.bash_profile

RUN apt-get install -y python3 python3-pip ffmpeg

RUN apt-get remove -y python2.7
RUN apt-get autoremove -y
RUN pip3 install -U ffmpeg-python pytz

COPY build/autocut.py /usr/local/bin/
