sudo apt update
sudo apt install python3-pip -y --fix-missing
pip install colorama
pip install psycopg2-binary
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql.service
