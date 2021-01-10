# Upgrade Firmare

## Compile the Source Code on Linux System

Run the following commands to complete the compiler directly.

-   gcc -o mtkdownload mtkdownload.c

## Run on the Linux System

Run the following commands directly.

-   ./mtkdownload \<com\> ROM_VIVA \<format\>

## Command Line Parameters

-   \<com\>: - /dev/ttyS0 - /dev/ttyS1 - /dev/ttyS2 - /dev/ttyS3 - /dev/ttyUSB0
    Represent the:COM1,COM2,COM3,COM4 and the USB serial port

## ROM_VIVA filename to upgrade

-   < format > parameter Y or N
    -   Indicate whether or not format file system.
    -   for example：./mtkdownload /dev/ttyUSB0 ROM_VIVA Y
        -   Indicate to upgrade SIM800 ROM_VIVA file, and format the file system by the USB serial port.
