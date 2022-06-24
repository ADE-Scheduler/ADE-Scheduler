FROM centos:centos7.9.2009


RUN yum -y update

# Install needed deps for python install
RUN yum -y groupinstall "Development Tools"
RUN yum -y install openssl-devel \
                   libffi-devel \
                   bzip2-devel \
                   sqlite-devel \
                   ncurses-devel \
                   libreadline5-dev \
                   wget

# Install Python 3.10
RUN wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
RUN tar xvf Python-3.9.10.tgz
WORKDIR "/Python-3.9.10"
RUN ./configure --enable-optimizations \
                --enable-loadable-sqlite-extensions
RUN make altinstall -j
RUN python3.9 -m pip install gnureadline
WORKDIR "/"

# Install Redis
RUN yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
RUN yum -y --enablerepo=remi install redis

# Install PostgreSQL
# RUN yum -y install postgresql-server postgresql-contrib
# TODO: make postgres work to get the same env as the prod server ?

# Install Node.js
RUN curl -sL https://rpm.nodesource.com/setup_16.x | bash -
RUN yum -y install nodejs

# Add dev user
RUN useradd -ms /bin/bash dev
USER dev

# Entrypoint
COPY entrypoint.sh /run/entrypoint.sh
ENTRYPOINT ["/run/entrypoint.sh"]
