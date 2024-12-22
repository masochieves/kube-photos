#!/bin/bash

python display.py &
streamlit run server.py &

wait