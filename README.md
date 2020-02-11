# Bluefind: Emergency Ad Hoc Networks

## Using Bluetooth to Share Locations in Disaster Scenarios

### By Freddie Brown, Year 3 Computer Science, University of Warwick

This project is investigating how a system could be developed to be used in an emergency scenario to share the locations of people who have survived a natural or man made disaster. These situations see a number of different problems arise, but one major one is that the emergency services struggle to locate people who might be trapped or lost. This project presents a solution whereby survivors devices will talk to each other, sending details about themselves to each other (device MAC address, location) and details of users that they have interacted with. This kind of routing is a sort of epidemilogical routing, or network flooding. By doing this, the emergency services can collect and use this data to aid their rescue efforts.

## Project

Included in this repository are 3 solutions, 2 of which are redudant. They are kept to show progress of the project. The working solution is under the folder `code/python`. To run the project, use the command `sudo python3 code/python/bluefind.py` to use it as a server, or use the command `sudo python3 code/python/blueclient.py` to run the device as a client, which will search for server devices. This project should be run from the root directory of the project.

Furthermore, this project uses a SQLite databse to store any data is collects from communicating with other devices. For this to work, a file called `find.db` needs to be created in the highest level of the project. After this is created, a file called `code/setup.sql` needs to be executed in the database to define the table needed. To do this in one, just run `setup.sh`.

## Libraries Needed

All of these libraries are available on `apt` and `python` version `3.7.3`:

- `libboost-all-dev`
- `libgtk2.0-dev`
- `libdbus-1-dev`
- `sqlite3`
- Python packages used are included in `requirements.txt`
