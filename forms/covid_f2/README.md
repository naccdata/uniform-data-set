# NACC Forms

This directory contains REDCap artifacts for a set of forms from the National Alzheimer's Coordinating Center.
The forms and these artifacts having been created through a collaboration of NACC with representatives of the Alzheimer's Disease Research Centers (ADRC).

## Licensing

- The forms included in this repository are copyrighted.
  Detailed copyright statements and usage restrictions are available on the [NACC website](https://naccdata.org/data-collection/guidelines-copyright).

- Non-ADRC researchers who wish to use the forms in this repository should [complete and return a permission request](https://files.alz.washington.edu/nacc-permission-form.pdf).

## Is this a release?

Yes, if this file is part of a directory extracted from a zip file downloaded from [Uniform-Data-Set](https://github.com/naccdata/uniform-data-set/releases).

Otherwise, no.
*The unreleased contents of the [Uniform-Data-Set](https://github.com/naccdata/uniform-data-set) repository should be considered a work in progress and should not be used for technical or clinical research decisions.*

## Directory structure

This directory contains the following files:

1. The REDCap project XML file (name ending in REDCAP.xml) in in CDISC ODM format.
2. The project data dictionary (name ending in .csv)
3. Subdirectories for each of the instruments of the project containing at least the `instrument.csv` file and possibly the `survey_settings.csv`.
3. The LICENSE file
4. This README file
5. The RELEASE_NOTES file

## Getting Started

- If you are able to load a new project into your REDCap instance, we suggest starting with loading the XML file.
- If you are interested in combining the instruments in different ways in REDCap, you should start with the individual instrument files.
- If you are not going to use REDCap at all, you can use the project data dictionary to get DED-like information for the forms.

### Loading as a project

The complete project can be imported into your REDCap instance by uploading the XML file.

An XML file is a file which contains an entire project (all instruments, fields, and project attributes including Survey Settings).

To upload the XML file to your REDCap instance:

1. Log into your REDCap instance.
2. Click `New project`.
3. Give the project a title, and in the Project Creation option section select `Upload a REDCap project XML file (CDISC ODM format)`
4. Click on `choose file` and select the XML file from this directory.
   Alternatively, drag and drop XML file from onto the `choose file` button.
5. Click `Create project` or `Request to create project`.

Once the project is created, you can access an overview of the project by clicking on the link `An overview of this project` in the left-hand navigation bar named Project Dashboards. 
For instructions on how to disseminate the survey, click the link for `Survey dissemination instructions`.

### Importing into a project

To add these forms to an existing project, you can import the CSV file from this directory. That file is the REDCap Data Dictionary of the above project.

If you want finer control, the subdirectories contain the data dictionaries and survey settings for individual instruments.
