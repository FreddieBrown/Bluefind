echo "Installing Libraries using APT"
sudo apt install -y libgtk2.0-dev libdbus-1-dev sqlite3
echo "Installing Python Requirements"
sudo pip3 install -r requirements.txt
echo "Setting up database"
touch find.db
sqlite3 find.db < code/setup.sql
echo "Done"