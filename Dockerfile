# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.10

# Keeps Python from generating .pyc files in the container
# ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
# ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt ./requirements.txt
RUN python3 -m pip install --upgrade pip -r requirements.txt


#Create workdir
WORKDIR /app
COPY . /app

#Expose port
EXPOSE 8501

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["streamlit", "run","app.py"]
