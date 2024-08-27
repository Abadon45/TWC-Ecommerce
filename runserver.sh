#!/bin/bash
export ENV=development
cd src
. bin/activate
python manage.py runserver