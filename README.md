## TrainTime 

TrainTime is a Python GUI application that displays real-time train information for the Dublin Area Rapid Transit (DART) service. It fetches data using the official Irish Rail API.

The user can:
- Select the station
- Filter by direction (northdound, southbound or both)
- Set a default station
- Specify a time window (in minutes) for upcoming departures 

The app uses the following libraries:
- PyQt6, xmltodict, xml.etree.ElementTree, requests

To run the application, move to the project folder and run:
python3 traintime.py

