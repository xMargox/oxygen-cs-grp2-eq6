FROM python:3.11

# Create app directory
WORKDIR /app

# Copy source code
COPY Pipfile Pipfile.lock /app/

COPY src /app

# Install app dependencies
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python", "main.py"]

