#!/bin/bash
mkdir build
rsync -R forms/$1/**/instrument.csv build/
rsync -R forms/$1/**/survey_settings.csv build/
rsync -R forms/$1/*.REDCap.xml build/
rsync -R forms/$1/*_data_dictionary.csv build/
rsync -R forms/$1/*.md build/
