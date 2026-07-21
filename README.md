<!-- <p align="center">
  <img width="50%" src="./static/imgs/cyberDefense_logo.png" alt="CyberDefense logo">
</p> -->

# WARNING: This document mainly reflects  version 1.0 of CyberDefense.  It may or may not be up-to-date.

See the wiki for additional more current information: https://github.com/zhida-li/CyberDefense/wiki

<h1 align="center">
  CyberDefense: Tool for Detecting Network Anomalies and Intrusions
</h1>

<h2 align="center">
  Anomaly detection tool that integrates various stages of the anomaly detection process
</h2>

<h4 align="center">
  Author: Zhida Li
</h4>

## About CyberDefense
The anomaly detection tool (**CyberDefense**) is used to detect BGP anomalous events based on routing records collected worldwide from major Internet exchange points. It also facilitates creating new machine learning models based on historical BGP anomalous events. **CyberDefense** integrates various stages of the anomaly detection process. The tool consists of: data download, real-time data retrieval, data container, feature extraction, feature extraction, label refinement, data partition, data processing, machine learning algorithms, hyper-parameter selection, machine learning models, and classification modules. It is based on Python and JavaScript as terminal-based or web-based application.
**CyberDefense** consists of **BGPGuard** and **ModelOcean** subsystems.

![](./static/imgs/cyberDefense.png)

The web-based **CyberDefense** version offers an interactive interface for monitoring and performing experiments. It includes several functions from the terminal-based application and is developed using additional programming languages, frameworks, and functions. 
Its front-end is built based on HTML, CSS ([Bootstrap](https://getbootstrap.com): an open-source CSS framework), and [Socket.IO](https://socket.io) (a transport protocol written in a JavaScript for real-time web applications). Its back-end is developed using [Flask](https://flask.palletsprojects.com/en/2.0.x) (a micro web framework written in Python).

## About BGPGuard Subsystem
**BGPGuard** is used for real-time anomaly detection or off-line data classification 
based on messages collected from [RIPE](https://www.ripe.net/analyse) or [Route Views](http://www.routeviews.org).
For real-time anomaly detection, BGP _update_ messages are retrieved, processed, and analyzed using available pre-trained models. 
The off-line classification is based on the specified start and end dates, times of 
the anomalous event, partitioning of the training and test datasets, and 
machine learning algorithms (GBDT, CNN, RNN, or [VFBLS](https://ieeexplore.ieee.org/document/9430511)).

Terminal-based: https://github.com/zhida-li/BGPGuard-terminal-app

## About ModelOcean Subsystem
**ModelOcean** enables processing various datasets such as NSL-KDD and CIC datasets to create models for various types of intrusion attacks such as DDoS, User to Root (U2R), Remote to Local (R2L), and probing. It has an additional module (data container) for custom datasets.

---

## Structure:

``` 
CyberDefense
├── LICENSE
├── README.md
├── app.py
├── app_offline.py
├── app_realtime.py
├── config.py
├── requirements.txt
├── database
│   ├── database.py
│   └── db_files
├── src
│   ├── __init__.py
│   ├── check_versions.py
│   ├── dataDownload.py
│   ├── data_partition.py
│   ├── data_process.py
│   ├── featureExtraction.py
│   ├── input_exp.txt
│   ├── label_generation.py
│   ├── progress.py
│   ├── progress_bar.py
│   ├── subprocess_cmd.py
│   ├── time_tracker.py
│   ├── CSharp_Tool_BGP
│   ├── STAT
│   ├── VFBLS_v110
│   ├── data_historical
│   ├── data_ripe
│   ├── data_routeviews
│   ├── data_split
│   ├── data_test
│   └── parmSel
│   └── playground
├── static
│   ├── css
│   │   └── style.css
│   ├── imgs
│   └── js
└── templates
    ├── bgp_ad_offline.html
    ├── bgp_ad_realtime.html
    ├── contact.html
    ├── index.html
    └── layout.html
```
The `src` directory contains the source code for the real-time detection and off-line classification tasks.
Various Python functions have been developed to implement and incorporate the anomaly detection steps.

---

## 🏗️ Getting Started with CyberDefense
###### Python 3.7 or Python 3.8

### External Libraries
The web-based **CyberDefense** version relies on additional external libraries. 
The external CSS and JavaScript libraries provided by [_jsDelivr_](https://www.jsdelivr.com) have been 
included in `layout.html`.

The Python libraries installed by [_pip_](https://pip.pypa.io/en/stable/) are:
- [_NumPy_](https://numpy.org): used to perform mathematical operations 
on multi-dimensional arrays and on matrices generated during the process.
- [_SciPy_](https://scipy.org): dependency of the _scikit-learn_ library. 
_SciPy_'s _zscore_: function used to perform normalization.
- [_scikit-learn_](https://scikit-learn.org/stable): employed for processing data and calculating performance metrics.
- [_PyTorch_](https://pytorch.org): used for developing deep learning models.

- [_Flask_](https://flask.palletsprojects.com/en/2.0.x): web framework based on _Werkzeug_
and _Jinja_.
(The _Flask_'s functions are used to transfer variables and render web pages. 
_Flask_ also processes the GET/POST requests from the front-end.)
- [_Werkzeug_](https://werkzeug.palletsprojects.com/en/2.0.x): web application library used to 
create a web server gateway interface (WSGI).
- [_Jinja_](https://jinja.palletsprojects.com/en/3.0.x): web template engine. Variables, statements, 
and expressions allowed to include in HTML files. 
- [_Flask-SocketIO_](https://flask-socketio.readthedocs.io/en/latest): offers bi-directional communications 
with low latency between the clients (front-end) and the server (back-end) for _Flask_ applications.
- [_python-socketio_](https://python-socketio.readthedocs.io/en/latest): implementation of the _Engine.IO_ in Python. 
- [_python-engineio_](https://github.com/miguelgrinberg/python-engineio): library for real-time communication 
between client and server based on WebSocket. 
- [_Eventlet_](https://eventlet.net): networking library for executing asynchronous tasks.

### Install the external Python libraries by running:
Note: virtual environment is recommended.
```bash
pip install -r requirements.txt
```

### The C# compiler should be installed prior to executing the BGP C# tool.
- [_Mono_](https://www.mono-project.com): an open source version of Microsoft .NET framework. 
Mono includes a C# compiler for several operating systems 
such as macOS, Linux, and Windows.

## 🚀 Launching CyberDefense
The Python file `app.py` is used to execute the application.
The following command is used to start the application:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Running on:
```bash
http://127.0.0.1:5000/
```

---
## 🎡 Playground
Sample code for gradient boosting machines may be run without launching the `app.py`:
```bash
./src/playground/gbdt_offline_sample
```
Please see details in `README.md`.

---
## 📚 License
The **CyberDefense** is open-sourced tool under the terms of the MIT license.
