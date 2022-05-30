# This is a Dockerfile to 'containerize' all proof points.
# The reason it was created is to eliminate the need for doing local pip install
# as well as eliminating local python virtual environments. 
FROM python:3.7
# move all the files into a container "app" folder
COPY ./proofs /proofs/
# set the workdir
WORKDIR /proofs
# install all the modules required for all proofs
RUN python3 -m pip install pymongo pymongo[srv] dnspython faker asyncio requests srvlookup python-dotenv boto3
CMD ["python3"]
# docker build . -t <image_name>
# docker run <image_name> python3 proofs/17/continious-insert.py