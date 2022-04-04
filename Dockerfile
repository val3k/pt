FROM python:3.8-buster

WORKDIR /app
COPY . .
ARG USER_GID=$USER_GID
ARG USER_UID=$USER_UID
ARG USERNAME=$USERNAME

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown $USERNAME /app

ENV PYTHONPATH="/app"

USER $USERNAME

ENV PATH="${PATH}:/home/${USERNAME}/.local/bin"
RUN pip3 install -r requirements.txt

CMD [ "streamlit", "run", "app.py"]
