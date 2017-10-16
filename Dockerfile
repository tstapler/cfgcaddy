FROM ruby:2.4

# Install python and dependencies
RUN apt-get update && apt-get install -y python python-dev python-pip
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY Gemfile /Gemfile
COPY Guardfile /Guardfile

RUN bundle install

COPY ./cfgcaddy /cfgcaddy/cfgcaddy
COPY ./setup.py /cfgcaddy/setup.py

RUN pip install --editable /cfgcaddy
