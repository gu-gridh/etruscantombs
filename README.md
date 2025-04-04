# Etruscan Tombs

This is the repository for the Django application of the Etruscan Tombs project, led by Jonathan Westin at GRIDH. This project is developed as an app in Diana. It is developed as an initial clone of the [Jubileum portal](https://github.com/gu-gridh/jubileum). Additional developers attached to the project are Matteo Tomasini and Tristan Bridge. This Diana application has been developed and is maintained by Matteo Tomasini. The public frontend of Etruscan Chamber Tombs is developed as a project within [Multimodal Map](https://github.com/gu-gridh/multimodal-map) (MuM), a repository of user interface modules developed by GRIDH specifically aimed at spatio-temporal visualisations. 



## Loading data

Photographic images can be uploaded as data models using the script

```bash
conda activate diana
python manage.py etruscantombs_load 
```

One can also specify a `folder` where data do be uploaded is stored, by adding `-b folder` to the second line. As a default, the data is stored in the `MEDIA_ROOT` as specified in the local settings. The filenames for each image need to follow the scheme `NNN_AuthorFirstName_AuthorLastName_YY-MM-DD_typeOfImage_xxxx.jpg` where `NNN` is the tomb name to which the image is associated, and `xxxx` a generic name of the picture that gets parsed but not used. For example for a picture attached to tomb #1: `001_Jonathan-Westin_2023-10-19_photograph_0000.jpg`.
The `typeOfImage` needs to correspond to one of the `TypeOfImage` classes in the data models.

The load script takes care of only uploading images that are not already uploaded on the database.

## Database and API documentation
The backend solution upon which The Etruscan Chamber Tombs portal is developed allows for consistent data input, and facilitates the interaction of end-users with the data shown in the frontend. To make the data open and reusable The Etruscan Chamber Tombs project makes available compliant REST APIs (including GeoJSON API), generated through the Django REST framework. These are the same APIs the projects's own frontend relies upon. Below follows a description of the APIs. [under construction]

### APIs
https://diana.dh.gu.se/api/etruscantombs/geojson/place/


## Datasets
### CTSG-2015 - Chamber Tombs of San Giovenale
This dataset is derived from the thesis The Chamber Tombs of San Giovenale and the Funerary Landscapes of South Etruria (2015) by Fredrik Tobin-Dodd.
