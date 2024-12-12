# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


ARG MONAI_IMAGE=projectmonai/monai:1.4.0

FROM ${MONAI_IMAGE}
LABEL maintainer="monai.contact@gmail.com"

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends ca-certificates build-essential \
        python3-gst-1.0 gstreamer1.0-python3-plugin-loader gstreamer1.0-plugins-base gstreamer1.0-tools gstreamer1.0-libav \
        gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
        gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/lib/python3.12/EXTERNALLY-MANAGED /usr/lib/x86_64-linux-gnu/*_static.a 

COPY . /opt/monaistream
RUN python -m pip install --upgrade --no-cache-dir pip \
    && python -m pip install /opt/monaistream
