
FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel                                                                                                                                                                                                
RUN python3 -m pip install -r ./requirements.txt  

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
# CMD [ "python3", "API.py"]