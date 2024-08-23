### Documentation for ADE-Scheduler Docker Setup

#### Dockerfile Overview

The Dockerfile sets up a Docker image for the **ADE-Scheduler** project, a Python web application running on Rocky Linux 8. The image is configured with all the necessary tools and dependencies. Key steps include:

1. **Base Image:**
   - Uses Rocky Linux 8 as the base operating system for the Docker image.

2. **System Updates and Dependency Installation:**
   - Updates system packages and installs development tools and libraries (such as OpenSSL, SQLite, etc.) required for building and running the software.

3. **Python Installation:**
   - Downloads and installs Python 3.9 from the source to ensure compatibility with the application’s codebase.

4. **Redis and PostgreSQL Installation:**
   - Installs Redis for caching and PostgreSQL for the database backend, both essential components for the backend infrastructure.

5. **Node.js Installation:**
   - Installs Node.js 16.x to manage JavaScript dependencies and run build tools like Webpack for front-end development.

6. **Create Non-root User:**
   - Adds a non-root user named `dev` to run the application securely without root privileges.

7. **Setup Application Directory:**
   - Sets the working directory to `/ADE-Scheduler` and copies the application code into this directory.

8. **Install Python and Node.js Dependencies:**
   - Installs `poetry` for managing Python dependencies and uses Node.js to install JavaScript dependencies and build frontend assets.

9. **Entrypoint Script:**
   - Specifies a custom entrypoint script (`entrypoint.sh`) to initialize the environment and start the application.

#### entrypoint.sh Overview

The `entrypoint.sh` script is executed when the Docker container starts. It performs several initialization tasks:

1. **Activate Python Virtual Environment:**
   - Activates the Python virtual environment to ensure all Python dependencies are isolated and managed properly.

2. **Install Python Dependencies with Poetry:**
   - Uses `poetry` to install Python modules as specified in the `pyproject.toml` file.

3. **Setup Environment Configuration:**
   - Checks for the presence of a `.flaskenv` file and creates one from a default template if it does not exist.

4. **Start Redis Server:**
   - Launches the Redis server in the background to handle caching tasks.

5. **Run Flask Database Initialization:**
   - Initializes the database for Flask using a simpler SQLite setup for development.

6. **Start Flask Application:**
   - Runs the Flask application, making the web server accessible on the specified port.

#### Docker Build and Run Commands

To build and run the ADE-Scheduler Docker container, use the following commands:

```bash
docker build -f Dockerfile -t ade-scheduler ..
docker run --name ade-scheduler -it -p 5000:5000 -v <Path to ADE-Scheduler folder>:/ADE-Scheduler ade-scheduler
docker start -i ade-scheduler       # To run the app
docker exec -it ade-scheduler bash  # To acces to terminal
       source /ADE-Scheduler/venv/bin/activate # once you have access to the bash execute this
       flask shell # to access to flask shell
```
