FROM gcr.io/google_appengine/python-compat-multicore

RUN apt-get update -yq

# Add app code
ADD . /app/

# Install requirements
RUN if [ -s requirements.txt ]; then pip install -r requirements.txt; fi
