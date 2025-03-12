# Use official Python image as the base
FROM python:3.10-slim

# Copy project requirements
COPY ./requirements.txt /requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /src

# Set working directory inside the container
WORKDIR /src

# Run migrations and start the development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
