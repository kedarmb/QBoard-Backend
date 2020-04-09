# pull official base image
FROM python:3.7

# set work directory
WORKDIR /code/

# set environment variables
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt /code/
RUN pip3 install --no-cache-dir -r requirements.txt

# copy project source code
COPY . /code/

#expose port for accessing
EXPOSE 8000

# Run app
CMD ["gunicorn", "Quark.wsgi", "--log-file", "-"]
