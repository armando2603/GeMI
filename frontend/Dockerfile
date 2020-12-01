FROM ubuntu

# set a directory for the app
WORKDIR /home/

# set a directory for the app
WORKDIR /home/master-thesis-demo/

# copy all the files to the container
COPY . .

ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt install --yes python3-pip
RUN pip3 install -r api/requirements.text
RUN apt install --yes npm
RUN npm i -g @quasar/cli
RUN npm install
#RUN npm rebuild node-sass
# define the port number the container should expose
EXPOSE 8080
EXPOSE 5000

# CMD quasar dev

