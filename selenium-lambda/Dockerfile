# Stage 1: Build dependencies
FROM public.ecr.aws/lambda/python@sha256:10dbb67ede15b5fd516be87dd71c3f7968904b0b840235720486476b34ef9b67 as build

# Install dependencies for downloading and extracting
RUN yum -y -q install unzip gzip tar bzip2 xz

# Set URLs and paths
ENV URL_FIREFOX="https://ftp.mozilla.org/pub/firefox/releases/141.0/linux-x86_64/en-US/firefox-141.0.tar.xz" \
    URL_GECKODRIVER="https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"

# Download and extract Firefox and GeckoDriver
# This is a more explicit and reliable way to ensure the files are in place.
RUN mkdir -p /tmp/download && \
    curl -Lo - ${URL_FIREFOX} | tar -Jxf - -C "/tmp/download/" && \
    curl -Lo - ${URL_GECKODRIVER} | tar -zxf - -C "/tmp/download/" && \
    ls -laR /tmp/download/ && \
    # Now, move the executables to a final location in the build stage
    mv /tmp/download/firefox/firefox /usr/local/bin/firefox && \
    mv /tmp/download/geckodriver /usr/local/bin/geckodriver && \
    chmod +x /usr/local/bin/firefox && \
    chmod +x /usr/local/bin/geckodriver && \
    # Cleanup
    yum clean all -y && \
    rm -rf /var/cache/yum

# Stage 2: Final image for Lambda
FROM public.ecr.aws/lambda/python@sha256:10dbb67ede15b5fd516be87dd71c3f7968904b0b840235720486476b34ef9b67

# Install dependencies required by Firefox
RUN yum -y -q install \
    gtk3 \
    libXScrnSaver \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXinerama \
    libXrandr \
    libXtst \
    pango \
    mesa-libGLU \
    libgudev1 \
    libXss \
    libXfixes \
    libXrandr \
    libXinerama \
    libXcursor \
    libXcomposite \
    libXdamage \
    libXtst \
    dbus-glib \
    dbus-libs \
    libgbm \
    libGL \
    libglvnd-glx \
    alsa-lib \
    # Cleanup
    && yum clean all -y \
    && rm -rf /var/cache/yum

# Install Python Dependencies
RUN pip install --no-cache-dir \
    boto3>=1.34 \
    pyvirtualdisplay>=3.0 \
    requests>=2.31.0 \
    beautifulsoup4==4.12.3 \
    selenium>=4.19

# Now, we copy from a single, final location in the build stage
COPY --from=build /usr/local/bin/firefox /usr/local/bin/firefox
COPY --from=build /usr/local/bin/geckodriver /usr/local/bin/geckodriver

# The PATH is already set to include /usr/local/bin

# Copy your application code and entrypoint script
COPY main.py ./
COPY entrypoint.sh ./

# Set permissions for the entrypoint script
RUN chmod +x entrypoint.sh

# Set the ENTRYPOINT and CMD for Lambda
ENTRYPOINT ["./entrypoint.sh"]
CMD [ "main.handler" ]