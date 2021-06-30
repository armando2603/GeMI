# GeMI Tool

Welcome to the Genomic Metadata Integration tool! with this web-tool is possible to extract structured tables from the metadata of all the experiments contained in the Gene Expression Omnibus.

<a href="https://www.youtube.com/watch?v=HLcDDIQ69YA" target="_blank"><img src="https://raw.githubusercontent.com/marcotcr/lime/master/doc/images/video_screenshot.png" width="450" alt="KDD promo video"/></a>

## Installation

- Install the last version of Docker
- Download the containers with the commands:
  ```console
  docker pull 2603931630/gemi:frontend
  ```
  ```console
  docker pull 2603931630/gemi:backend
  ```
- Download the repository:
  ```console
  git clone https://github.com/armando2603/gemi
  ```
- Install the nodes.js dependencies:
  ```console
  docker run --rm -it -v "/$(pwd)/gemi/frontend/:/usr/src/app/" -p 51111:8080 2603931630/gemi:frontend npm install
  ```
- Run the containers:
  ```console
  docker run -d --rm -it -v "/$(pwd)/gemi/frontend/:/usr/src/app/" -p 51111:8080 2603931630/gemi:frontend quasar dev && docker run -d -v "/$(pwd)/gemi/backend/:/workspace/" -p 51113:5003 -it --rm --gpus all 2603931630/gemi:backend flask run -p 5003 -h 0.0.0.0
  ```
- 
Remember that you need a gpu NVIDIA in your machine
