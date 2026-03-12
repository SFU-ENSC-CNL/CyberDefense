# docker-compose-CyberDefense

#### Just a docker-compose structure for CyberDefense ([https://github.com/zhida-li/CyberDefense](https://github.com/zhida-li/CyberDefense))

### For **installation**, please follow the instructions:

1. Install Docker, instructions available: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

2. Clone this repository
```
     git clone https://github.com/luizsoliveira/docker-compose-CyberDefense
     cd docker-compose-CyberDefense
```

3. Clone the CyberDefense repository into the **app** folder
```
    git clone https://github.com/zhida-li/CyberDefense app/CyberDefense
```
4. Inside the **main docker-compose project** folder, start docker-compose using the following command:
```
     docker-compose up
```
5. Open your browser at the following URL: [http://localhost:5001](http://localhost:5001)
6. Have fun and good research!

### In case of CyberDefense **code changes**, please follow the instructions:

1. Inside the **main docker-compose project** folder, stop the container (if is started), build the **cyberdefense-python-dev** image, and start the container again by running the following commands:
```
     docker-compose down
     docker-compose build
     docker-compose up
```
2. Open your browser at the following URL: [http://localhost:5001](http://localhost:5000)
3. Have fun and good research!
