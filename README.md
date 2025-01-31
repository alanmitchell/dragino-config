# dragino-config

Configuration scripts for Dragino LoRaWAN sensors.

Some Notes on usage:

* Adding the Dragino sensor into the Things Network *first* makes for a smoother
configuration process.  If the sensor is repeatedly trying to join the network,
serial configuration commands are often rejected due to the sensor processor being busy.
If you enter the sensor into Things, then it will join and be ready to receive
configuration commands.
    * Taking a picture of the label on the Dragino box, and then allowing the Lens 
    feature of Google Photos to recognize the text in the label is useful.  You then
    can copy and paste the Dev EUI, App EUI and App Key into the Things setup screen.

* For use of the scripts in this repository, a couple intial steps are required:
    * Install the `uv` utility for managing Python projects.
    * Change into the directory on your computer containing the repository files.

* Run the script:

    ```
    uv run configure_rs485.py <COM port>
    ```
    where "\<COM port\>" is the name of the serial port, e.g. "COM4".

* For developers: to create a standalone executable of the script, run:

    ```
    uv run pyinstaller -F configure_rs485.py
    ```
    The installer will be found in the /dist directory

* For manual configuration with a Serial Terminal program (without use of this script), 
programs such as CuteCom (Linux) or YAT (Windows) are easiest to
use, because they allow you to prepare command (and edit if needed) before sending
it to the Dragino device.  They send the entire line at once to the device. Programs
like Putty send each character as you type it, and if you make a mistakes, you cannot
correct it as it has already been sent.  Also, CuteCom and YAT keep a history of past
commands and allow you to retrieve them for reseding, or editing and resending.
    * Remember that AT commands will not excecute unless the password is entered; the password defaults to "123456".
