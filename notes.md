# Notes on Configuring Dragino Sensors

* Adding the Dragino sensor into the Things Network *first* makes for a smoother
configuration process.  If the sensor is repeatedly trying to join the network,
serial configuration commands are often rejected due to the sensor processor being busy.
If you enter the sensor into Things, then it will join and be ready to receive
configuration commands.
    * Taking a picture of the label on the Dragino box, and then allowing the Lens 
    feature of Google Photos to recognize the text in the label is useful.  You then
    can copy and paste the Dev EUI, App EUI and App Key into the Things setup screen.

* For manual configuration with a Serial Terminal program, programs such as 
CuteCom (Linux) or YAT (Windows) are easiest to
use, because they allow you to prepare command (and edit if needed) before sending
it to the Dragino device.  They send the entire line at once to the device. Programs
like Putty send each character as you type it, and if you make a mistakes, you cannot
correct it as it has already been sent.  Also, CuteCom and YAT keep a history of past
commands and allow you to retrieve them for reseding, or editing and resending.

* For use of the scripts in this repository, a couple intial steps are required:
    * Make sure Python 3.9 or greater is installed.
    * Change into the directory on your computer containing the repository files.
    * Copy the `config_example.py` file to `config.py`, which is the file that will
    actually be used by the configuration script.  Edit the contents of `config.py`
    appropriately, for example entering the correct identifier for the Serial port where
    the Dragino sensor is connected.
    * Install the necessary Python libraries by executing `pip install -r requirements.txt`.

* Run the script, for example:

    ```
    python configure_rs485.py
    ```
