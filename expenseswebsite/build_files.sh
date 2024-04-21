python 3 -m pip install -r requirements.txt
python 3 manage.py makemigrations --noinput
python 3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput