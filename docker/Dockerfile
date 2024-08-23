# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update repository URLs to point to Rocky Linux repositories
RUN dnf -y update && \
    dnf -y install epel-release

# Install necessary development tools and dependencies
RUN dnf -y groupinstall "Development Tools" && \
    dnf -y install openssl-devel libffi-devel bzip2-devel sqlite-devel ncurses-devel readline-devel wget curl

# Install Python 3.9 from source
RUN wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz && \
    tar xvf Python-3.9.10.tgz && \
    cd Python-3.9.10 && \
    ./configure --enable-optimizations --enable-loadable-sqlite-extensions && \
    make altinstall -j && \
    cd .. && \
    rm -rf Python-3.9.10*

# Install Redis from the official repository
RUN dnf -y install https://rpms.remirepo.net/enterprise/remi-release-8.rpm && \
    dnf -y --enablerepo=remi install redis

# Install PostgreSQL
RUN dnf -y install postgresql-server postgresql-contrib

# Install Node.js 16.x
RUN curl -sL https://rpm.nodesource.com/setup_16.x | bash - && \
    dnf -y install nodejs

# Create a non-root user for running the application
RUN useradd -m dev
USER dev

WORKDIR /ADE-Scheduler

# Copy application code
COPY --chown=dev:dev . /ADE-Scheduler/

# Install poetry and modify the PATH
RUN curl -sSL https://install.python-poetry.org | python3.9 - && \
    echo 'export PATH="/home/root/.dev/bin:$PATH"'

# Update & install Node deps (& run Webpack)
RUN npm install && \
    npx webpack --progress --watch --no-stats &

# Update & install Python deps
RUN python3.9 -m venv venv && \
    source /ADE-Scheduler/venv/bin/activate && \
    /ADE-Scheduler/venv/bin/python3.9 -m pip install --upgrade pip

# Execute poetry lock
RUN source ~/.bashrc && \
    poetry lock

# Set the entrypoint script
COPY ./docker/entrypoint.sh /run/entrypoint.sh
ENTRYPOINT ["/run/entrypoint.sh"]
