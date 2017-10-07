FROM continuumio/anaconda3

RUN pip install configparser
RUN conda install matplotlib
RUN pip install pyqt5

ADD problem2.py /

ENTRYPOINT [ "python", "problem2.py" ]
