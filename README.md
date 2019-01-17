# How to create a text-based CAPTCHA solving engine
 
This is a how-to guide for creating a CAPTCHA solving AI model that can be used to solve text-based CAPTCHAs as discussed in the following [blog](https://labs.mwrinfosecurity.com/blog/captcha22/). Two helper scripts are provided that can aid in the CAPTCHA-labeling process.

## Dependencies

The following Python packages are required to create the model:
* Tensorflow - [High Performance Numerical Computation](https://www.tensorflow.org/)
* AOCR - [Attention Optimal Character Recognition model](https://github.com/emedvedev/attention-ocr)
* CV2 - [OpenCv](https://opencv.org/) for reading and viewing images (Optional for helper scripts)
* Glob - For file management (Optional for helper scripts)

Each of these packages can be installed using:

```
pip install <package_name>
```

For the final step, AOCR Model Deployment, [Tensorflow Serving](https://github.com/tensorflow/serving) is also required. The simplest installation is via APT. The steps can be found [here](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/setup.md).

## CAPTCHA Solving Process

The CAPTCHA solving process consists of six steps:

1. CAPTCHA Retrieval
2. CAPTCHA Labeling
3. AOCR Dataset Generation
4. AOCR Model Training
5. AOCR Model Validation
6. AOCR Model Deployment


### 1. CAPTCHA retrieval

In order to train the AOCR model, examples of the CAPTCHA are required. Ideally, an initial testing dataset should consist of 500 CAPTCHAs where 450 will be used for training and 50 for validation. If the initial results indicate that the process is successful, these values can be increased to further improve the accuracy of the model.

The location of the CAPTCHA implementation will determine the retrieval process. Ideally, you want to look for the request used to retrieve the CAPTCHA. Once you have this link, you should be able to perform an iterative `wget` request to retrieve and save the required number of CAPTCHAs. The naming convention for these downloads does not really matter since the CAPTCHAs will be renamed after labeling.

### 2. CAPTCHA Labeling

The CAPTCHA labeling process requires the most effort and time. A helper script, `captcha_labeling_script.py`, is provided to assist with this process.

The script can be used by executing:

```
python catcha_labeling_script.py <directory with CAPTCHAs> <directory to store labeled CAPTCHAs>
```

The script will show the CAPTCHAs one by one requesting input from the user for the label of the CAPTCHA. The user can press `-` to end the current label or `` ` `` to end the labeling session. For each entered label, the CAPTCHA will be saved with the label as the name and the unlabeled CAPTCHA image will be removed.

### 3. AOCR Dataset Generation

Training and validation datasets have to be created for the AOCR model. The `label_generating_script.py` helper script can be used to generate the dataset if the `captcha_labeling_script.py` was used to label the CAPTCHA.

The script can be used by executing:

```
python label_generating_script.py <directory where CAPTCHAs are stored> <directory to store label file>
```

The output from the script would be a label file, `label.txt`, with the names and answers for each of the CAPTCHAs. The contents of this file should be split into two, namely `train_labels.txt` and `test_labels.txt`. It is recommended that roughly 10% of all data is used for testing. If 500 CAPTCHAs were labeled, copy 450 of the lines of `label.txt` to `train_labels.txt` and the remaining 50 lines to `test_labels.txt`.

These files will have to be converted into the `tfrecords` format for the AOCR model. Copy the two files into the directory where the CAPTCHAs are stored and from the directory execute the following:

```
aocr dataset train_labels.txt training.tfrecords
aocr dataset test_labels.txt testing.tfrecords
```

### 4. AOCR Model Training

The AOCR model will have to be trained. This can be done by executing the following:

```
aocr train training.tfrecords
```

Remember to include and set the `--max-width` and `--max-height` values depending on the size of the CAPTCHA used.

The `loss` and `perplexity` values should be reviewed during training. Ideally the `perplexity` will fall to 1.00 and the `loss` should drop below 0.002. The model will auto-save every 100 steps. Once sufficient `loss` and `perplexity` values have been reached, the training can be stopped by simply pressing `Ctrl^C`. Training can also be continued later by just running the same command. It is recommended that for every 500 steps, training is stopped, and a validation round is performed. 

### 5 AOCR Model Validation

Validation of the AOCR model is required to determine if the model has successfully learnt the features and text of the CAPTCHA. Validation can be done by executing the following:

```
aocr test testing.tfrecords
```

The same values of `--max-width` and `--max-height` used for training should be provided for the validation step. The validation step will provide four readings per CAPTCHA namely:

1. `Accuracy` - The accuracy of the entire image prediction. 100% indicates that all character were successfully predicted.
2. `Probability` - The certainty of the model that the provided prediction is correct. This can be used to filter predictions of a trained model to improve submission accuracy. 
3. `Loss` - A higher loss indicates a bigger discrepancy between the learnt model and the validation data.
4. `Perplexity` - A higher perplexity indicates that the validation data is "new" to the model and it hasn't learnt or seen anything like it before.

The results can then be reviewed. The 100% accuracy hits are the CAPTCHAs that the model was able to correctly predict. A high number of these indicates positive results for completely solving the CAPTCHA. More data can be used to further increase the accuracy of the model.

The model will indicate the actual and predicted answer for CAPTCHAs were the entire CAPTCHA could not be predicted. A review of these results will indicate what characters the model is currently confusing. The most common are `l` and `i` as well as `n` and `m`. If there are any incorrect predictions that do not make logical sense, such as `C` being predicted as `X`, review the labeled data as it could be that some of the labels are incorrect.

If almost no testing samples are solved 100%, it could indicate that the noise in the CAPTCHA is too high and hence a pre-processing step is required. This will depend on the specific CAPTCHA. Additionally, more training samples, or even more training steps, can also improve the accuracy.

### 6 AOCR Model Deployment

If a sufficiently accurate model could be trained, the model should be deployed to a Tensorflow server for use. The model will have to be extracted first and can be done by executing:

```
aocr export exported-model
```

Copy the contents of the `exported-model` folder into a sub-folder named `1`. The exported model can now be deployed using a Tensorflow model server.

To create the server, execute the following command:

```
tensorflow_model_server --port=9000 --rest_api_port=9001 --model_name=<yourmodelname> --model_base_path=<full path to exported model directory>
```

To make use of this model, a curl request with a base64 encoded CAPTCHA can be used. Such as the following example:

```
curl -X POST \
  http://localhost:9001/v1/models/yourmodelname:predict \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{
  "signature_name": "serving_default",
  "inputs": {
     	"input": { "b64": "/9j/4AAQ==" }
  }
}'
```

The server would then respond with the CAPTCHA answer as well as prediction certainty. To increase submission accuracy, the prediction certainty can be used as filter value to discard any CAPTCHAs with a prediction below a chosen certainty.

































