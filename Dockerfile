FROM gcr.io/google_appengine/python-compat-multicore

# Install scipy dependences
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python-tk python-numpy python-scipy python-matplotlib python-crcmod python-lxml

# Add app code
ADD . /app/

# Install requirements
RUN if [ -s requirements.txt ]; then pip install -r requirements.txt; fi
