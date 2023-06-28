FROM python:3.8

# Create app directory
WORKDIR /usr/src/app

# Copy source code
COPY . .

# Install app dependencies
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python", "main.py"]

