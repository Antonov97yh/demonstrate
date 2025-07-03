#!/bin/bash

# docker run -p 8501:8501 innprak
docker run -v /home/pavel/sklonnost_klientov_k_produktam/source:/sklonnost_klientov_k_produktam/source -p 8501:8501 --name systemctl_container innprak
