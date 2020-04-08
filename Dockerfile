# pull official base image
FROM alpine:3.7
RUN apk add --update python py-pip

# set work directory
WORKDIR /code/

# set environment variables
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# copy project source code
COPY . /code/

#expose port for accessing
EXPOSE 8000

# Run app
CMD ["gunicorn", "Quark.wsgi", "--log-file", "-"]
