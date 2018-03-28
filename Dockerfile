#looks at requirments.txt and builds your python environment
FROM python:2.7-onbuild

#set path so scripts can be called easily
ENV PATH="/usr/src/app/calc/DRL_bin:/usr/src/app/calc:${PATH}"
ENV PYTHONPATH="/usr/src/app/calc:/usr/src/app/www"
#
#opens a shell with -it  
CMD ["/bin/bash"]

