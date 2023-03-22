# R 4.2.1
FROM rocker/verse:4.2.1

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
         locales \
         libcurl4-openssl-dev \
         libssl-dev \
        imagemagick \
        libmagick++-dev \
        gsfonts \
        pandoc \
        libicu-dev \
        libtcl8.6 \
        libtk8.6 \
        biber \
        git-lfs \
        git \
        curl \
        wkhtmltopdf \
        pip \
        && rm -rf /var/lib/apt/lists/* \
        && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8


COPY install.R .
RUN R CMD BATCH install.R

# Install the necessary Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt


