<p align="center">
    <img src="https://raw.githubusercontent.com/FSecureLABS/captcha22/master/images/CAPTCHA22.svg" width="500px">
</p>

> **CAPTCHA22** is a toolset for building, and training, CAPTCHA cracking models using neural networks. These models can then be used to crack CAPTCHAs with a high degree of accuracy. When used in conjunction with other scripts, CAPTCHA22 gives rise to attack automation; subverting the very control that aims to stop it.

### Table of contents 

- [Installation](#installation)
    - [Prerequisites](#prerequisites)
- [Usage: How to crack CAPTCHAs](#usage-how-to-crack-captchas)
    - [Step 1: Creating training sample data (labelling CAPTCHAs)](#step-1-creating-training-sample-data-labelling-captchas)
    - [Step 2: Training a CAPTCHA model](#step-2-training-a-captcha-model)
    - [Step 3: CAPTCHA Cracking](#step-3-captcha-cracking)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)



## Installation

_CAPTCHA22 requires [tensorflow](https://github.com/tensorflow/tensorflow) (see [prerequisites](#prerequisites))._ You can then install CAPTCHA22  using `pip`:

```bash
pip install captcha22
```

### Prerequisites

CAPTCHA22 is most performant on a GPU-enabled tensorflow build. This, however, will require numerous steps (as discussed [here](https://www.tensorflow.org/install/gpu)). 

* To install a less optimal, CPU-based, tensorflow build - you can simply issue the following command:

    ```bash
    pip install "tensorflow<2"
    ```

* The tensorflow [serving](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/setup.md#installation-1) addon is required to host trained CAPTCHA models.

## Usage: How to crack CAPTCHAs

CAPTCHA22 works by training a neural network against a sample of labelled CAPTCHAs (using a sliding CNN with a LSTM module). Once this model is suitably accurate, it can be applied to unknown CAPTCHAs - automating the CAPTCHA cracking process. 

This process is broken down into 3 steps: 

### Step 1: Creating training sample data (labelling CAPTCHAs)

The first step in this whole process is create a sample of correctly labelled CAPTCHAs. Ideally, you'll want to aim for at least 200.

#### 1. Collecting CAPTCHAs 

Unfortunately, there is no *one size fits all* solution for collecting CAPTCHA samples and you'll have to be innovative with your approach. In our experience, we've had little difficulty automating this process using `wget` or the python `requests` library. How you approach this is up to you, but a good starting point would probably be to try and work out how the target application is generating/serving their CAPTCHAs. 

#### 2. Labelling

Sadly, labelling is manual. This is most laborious and time consuming step in this whole process - fortunately things only get better from here. To try and make things a little easier, we've included functionality to help with labelling: 

```bash
captcha22 client label --input=<stored captcha folder>
```

Once complete, CAPTCHA22 will produce a ZIP file (e.g. `<api_username>_<test_name>_<version_number>.zip`) that you can upload (discussed in [step 2](#upload-captcha-training-samples)). 

### Step 2: Training a CAPTCHA model 

Once you have a sample set of labelled CAPTCHAs, the next step is to begin training the CAPTCHA model. 

#### 1. Launch the Server (and API)

To do this, you first need to launch CAPTCHA22's server engine, which will poll the `./Unsorted/` directory for new ZIPs: 

```bash
captcha22 server engine
```

Enable the API for interfacing with the CAPTCHA22 engine (if you're an advanced user, feel free to skip this step):

```
captcha22 server api
```

*The default API credentials are `admin:admin`. You can modify the `users.txt` file to change this value, or add additional users. See the below code snippet for guidance:*

```bash
python -c "from werkzeug.security import generate_password_hash;print('username_string' + ',' + generate_password_hash('password_string'))"
```

#### 2. Upload CAPTCHA training samples

To upload training samples, simply drop the ZIP file you created in [Step 1](#labelling) into `./Unsorted/`. Alternatively, if you opted to enable the API, you can perform this step interactively using the client: 


```bash
captcha22 client api
```

In both cases, CAPTCHA22 will automatically begin training a model. 

#### 3. Deploy the trained model 

Once a model is trained and sufficiently accurate, the model can be deployed to use for automated cracking. The model can either be deployed on the CAPTCHA22 server or downloaded. Both methods can be performed using the interactive API client.

To host the model, extract the ZIP and execute:

```bash
tensorflow_model_server --port=9000 --rest_api_port=9001 --model_name=<yourmodelname> --model_base_path=<full path to exported model directory>
```

The interactive API client can also be used to upload a CAPTCHA to CAPTCHA22 to be solved by the hosted model. 

*The following cURL request will verify whether the model is working:*

```bash
curl -X POST \
    http://localhost:9001/v1/models/<yourmodelname>:predict \
    -H 'cache-control: no-cache' \
    -H 'content-type: application/json' \
    -d '{
            "signature_name": "serving_default",
            "inputs": 
            {
                "input": { "b64": "/9j/4AAQ==" }
            }
        }'
```

### Step 3: CAPTCHA Cracking

Once a model is hosted, you'll be able to pass CAPTCHAs to the model and receive an answer (i.e. automation). You can use the template code below to use CAPTCHA22 in conjuntion with your own custom code to execute a variety of automated attacks (e.g. _Username enumeration_, _Brute force password guessing_,  _Password spraying_, etc.).

```python
from captcha22 import Cracker

# Create cracker instance, all arguments are optional
solver = Cracker(
    #  server_url="http://127.0.0.1",
    #  server_path="/captcha22/api/v1.0/",
    #  server_port="5000",
    #  username=None,
    #  password=None,
    #  session_time=1800,
    #  use_hashes=False,
    #  use_filter=False,
    #  use_local=False,
    #  input_dir="./input/",
    #  output="./output/",
    #  image_type="png",
    #  filter_low=130,
    #  filter_high=142,
    #  captcha_id=None
    )

# Retrieve captcha from website
...
# Create b64 image string
...

# Solve with CAPTCHA22
answer = solver.solve_captcha_b64(b64_image_string)

# Submit answer to website and launch attack
...
```

As the model exposes a JSON API, you're not restricted to Python if you prefer to use tools such as cURL, wget, or anything else.

Two example cracker scripts are also provided (`baseline` and `pyppeteer`). Both of these scripts are experimental and will not cater for most cases.

* The `baseline` script will create a connection to the CAPTCHA22 server, or a locally hosted model, before requesting the file path to a CAPTCHA. 
* The `pyppeteer` script will use the baseline script and simulate browser requests to find and solve the CAPTCHA, before running a login attack.

To execute one of these scripts:
 
```bash
captcha22 client cracking --script=<script name>
```

## Troubleshooting

CAPTCHA22 was tested on two GPU-enabled Tensorflow rigs with the following specifications:

|                    | Rig 1             | Rig 2            |
| ------------------ | ----------------- | ---------------- | 
| **Graphics Card**  | GeForce GTX 1650  | GeForce GTX 960  |
| **OS**             | Ubuntu 16.06      | Ubuntu 16.04     |
| **Cuda Lib**       | Cuda 10.0.130     | Cuda 9.1.1       |
| **cuDDN Lib**      | cuDNN 10.0        | cuDNN 7.0        |
| **Tensorflow**     | Tensorflow 1.10.1 | Tensorflow 1.4.1 |

*For assistance on any issues in CAPTCHA22 itself, please log an issue.*

## Contributing

See [`CONTRIBUTING.md`](https://github.com/FSecureLABS/captcha22/CONTRIBUTING.md) for more information.

## License 

MIT License

Copyright (c) 2020 F-SECURE

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
