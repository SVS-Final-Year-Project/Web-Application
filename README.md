# KIDNEY CYST CLASSIFICATION

This web application allows you to predict the presence of cyst in kidney in real time using CT scan image.

MongoDB and Firebase are used as databases. 

## Workflow

The patient details and CT scan image are taken as input and the image is stored in firebase. The scan image is pre-processed and is given as input to the pre-trained deep learning models of CNN (ResNet50,InceptionV3 and Xception). The resulting prediction score from each model along with the URL of the image from firebase is used to generate a report stating the presence of cyst. 

There are 2 flow of authorization in this - General access and Admin access

With the general access, only the prediction can be made while with the admin access the generated report could be viewed, emailed and downloaded as well by converting the HTML template into a pdf with the help of wkhtmltopdf software.

- To generate report download the [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) software locally

- Add the saved model files as inceptionModelFile, xceptionModelFile and resnetModelFile

## Add environment file with following variables for firebase storage and secret key

- API_KEY
- AUTH_DOMAIN
- PROJECT_ID
- STORAGE_BUCKET
- MESSAGING_SENDER_ID
- APP_ID
- DATABASE_URL
- SECRET_KEY


## Authors

- [@Srivatsan](https://www.github.com/srivatsan2607)

