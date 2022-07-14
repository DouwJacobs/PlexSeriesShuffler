FROM python:3.8
ADD ./SeriesShuffler /workdir
WORKDIR /workdir
RUN pip install -r /workdir/requirements.txt
CMD python main.py