#!/bin/bash

Docker/build.sh && sudo systemctl stop sklonnost_klientov_k_produktam_eto_nazvaniye_dolzno_resat_glasa && sudo systemctl start sklonnost_klientov_k_produktam_eto_nazvaniye_dolzno_resat_glasa && sudo systemctl is-active sklonnost_klientov_k_produktam_eto_nazvaniye_dolzno_resat_glasa
