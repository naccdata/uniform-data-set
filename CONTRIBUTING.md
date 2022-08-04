# Contributing

## Git workflow

In limited scenarios, you can add or edit files on GitHub, but in general you will need to [use Git](https://docs.github.com/en/get-started/using-git) to manage your changes and share them to the repository.
An [example of contributing to an existing repository](https://docs.github.com/en/get-started/using-git/about-git#example-contribute-to-an-existing-repository) is given in those documents.

The steps there are:
1. Clone the repository and change into the directory.
2. Create a new branch for your changes.
3. Switch to the new branch.
4. Make whatever changes are needed.
5. Add the changes to the branch.
6. Commit the changes.
7. Push the branch to GitHub.


## Documentation

Documentation is stored in the `docs` directory.

### Creating/Editing Markdown Documentation
You can do this either with a local clone, or by creating and editing files directly in the browser.

For details on working in the browser, see
* [Creating new files](https://docs.github.com/en/repositories/working-with-files/managing-files/creating-new-files), and
* [Editing Files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files).

> Note: When you are done with your edits, under **Commit Changes** you should edit the commit message, and then choose "Create a new branch for this commit and start a pull request"

Create new documents as Markdown files (a file with a `.md` extension) in the `docs` directory.
Use the [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
format to make sure they display correctly on the site.

More detail on writing documentation on GitHub is available under **Writing on GitHub** in the GitHub [Get Started](https://docs.github.com/en/get-started) docs.

### Using Word files

To add or modify Word documents, you will need to follow the Git workflow above.

To **add** a document

1. Create and switch to a new branch with a descriptive name for the addition.
2. Place your document in the `docs` directory of this repository.
3. Add the document with git, commit the changes, and push the branch.

To **modify** a document in a branch

1. Checkout the branch
2. Open the word document from the docs directory in your clone, and save your work
3. Add the document with git, commit the changes, and push the branch.


## Forms

Forms are stored in a directory for each form set.
This directory contains the XML export and data dictionary for the REDCap project, 
along with subdirectories for each instrument of the project.
These instruments correspond to the individual forms and any other instruments in the project.

For instance, the Down Syndrome project looks like

```bash
forms/ds
├── DownSyndromeModule.REDCap.xml
├── DownSyndromeModule_data_dictionary.csv
├── a1d
├── b1d
├── b2d
├── c1d
├── d1d
└── formheader
```

The directory for each instrument contains the exported instrument files

```bash
forms/ds
└── a1d
    ├── OriginID.txt
    ├── instrument.csv
    └── survey_settings.csv
```

plus any documentation files that accompany the form.
These may include form PDFs, and quality rules for the form in a CSV.

### Adding forms

To add a new form set, follow the Git workflow to create and switch into a new 
branch with a name that indicates which forms are being added.

1. If it does not already exist, create a directory for the form set, use a 
   lowercase abbreviation for the name.
   Examples of existing names are `ds` for the Down Syndrome Module, and `uds` 
   for the UDS.
2. If a REDCap project for the forms already exists, export both the XML and
   data dictionary (CSV) for the project and place them in the top directory.
   Then export each individual instrument and add the exported files to the 
   directory.
   Instruments are exported as zip files, which will uncompress to a directory.
   Move this directory into the form set directory and rename to the (lowercase)
   name of the form.
3. Add and commit the new files to the branch.

> Note: if at any point you have a directory that doesn't have any contents,
add an empty file named `.gitkeep` to the directory and commit the file


## Tools


