# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app


COPY ../requirements.txt .
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 80
CMD ["fastapi", "run", "main.py", "--port", "80"]

#CMD ["mainLambda.lambda_handler"]