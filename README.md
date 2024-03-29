# Bluefind: Emergency Ad Hoc Networks

## Using Bluetooth to Share Locations in Disaster Scenarios

### By Freddie Brown, Year 3 Computer Science, University of Warwick

This project is investigating how a system could be developed to be used in an emergency scenario to share the locations of people who have survived a natural or man made disaster. These situations see a number of different problems arise, but one major one is that the emergency services struggle to locate people who might be trapped or lost. This project presents a solution whereby survivors devices will talk to each other, sending details about themselves to each other (device MAC address, location) and details of users that they have interacted with. This kind of routing is a sort of epidemilogical routing, or network flooding. By doing this, the emergency services can collect and use this data to aid their rescue efforts.

## Project

Included in this repository are 3 solutions, 2 of which are redudant. They are kept to show progress of the project. The working solution is under the folder `code/python`. To run the project, use the command `sudo python3 code/bluefind/bluefind.py` to use it as a server, or use the command `sudo python3 code/bluefind/blueclient.py` to run the device as a client, which will search for server devices. This project should be run from the root directory of the project.

Furthermore, this project uses a SQLite databse to store any data is collects from communicating with other devices. For this to work, a file called `find.db` needs to be created in the highest level of the project. After this is created, a file called `code/setup.sql` needs to be executed in the database to define the table needed. To do this in one, just run `setup.sh`.

When running the client side, the user has a choice of actions. Each of these actions will cause the client node to perform different actions when interacting with a server. These are spceified as a command line argument. Currently, there are 2 different modes:

- `normal`: Normal behaviour of the client. Will read and write information to/from the server
- `emergency`: Node acts as an emergency services node. For this, it will only read information from a server node.
- `secure`: Normal behaviour except there is a key exchange that occurs between client and server first, then all communication after that is encrypted.

## Libraries Needed

All of these libraries are available on `apt` and with `python` version `3.7.3`:

- `libgtk2.0-dev`
- `libdbus-1-dev`
- `libgirepository1.0-dev`
- `libcairo2-dev`
- `sqlite3`
- Python packages used are included in `requirements.txt`

## Tests

To run the tests of the project, navigate to `code/` and then run `pytest` which will run all tests. This will perform them on parts of the module which don't do any BLE specific stuff, as those tests will be more complex.
