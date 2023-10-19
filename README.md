# Etruscan Tombs

This is the repository for the Django application of the Etruscan Tombs project, led by Jonathan Westin at GRIDH. This project is developed as an app in Diana. It is developed as an initial clone of the [Jubileum portal](https://github.com/gu-gridh/jubileum). The developers attached to the project are Matteo Tomasini and Tristan Bridge.

This Diana application has been developed and is maintained by Matteo Tomasini

## Loading data

Photographic images can be uploaded as data models using the script

```bash
conda activate diana
python manage.py etruscantombs_load 
```

One can also specify a `folder` where data do be uploaded is stored, by adding `-b folder` to the second line. As a default, the data is stored in the `MEDIA_ROOT` as specified in the local settings. The filenames for each image need to follow the scheme `NNN_AuthorFirstName_AuthorLastName_YY-MM-DD_typeOfImage_xxxx.jpg` where `NNN` is the tomb name to which the image is associated, and `xxxx` a generic name of the picture that gets parsed but not used. For example for a picture attached to tomb #1: `001_Jonathan-Westin_2023-10-19_photograph_0000.jpg`.
The `typeOfImage` needs to correspond to one of the `TypeOfImage` classes in the data models.

The load script takes care of only uploading images that are not already uploaded on the database.
