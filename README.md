# AnkiRelay
Relay for using [Anki Vector](https://www.anki.com/en-us/vector) robots with NetsBlox

Requires `anki_vector` Python package, and a NetsBlox server with the `anki-vector` RPC.

# Setup

Vector robots must be set up for use with the SDK. The serial numbers of the robots must be added to the `.robots` file for the relay to know it should attempt to command them.

A `.env` file must be created with the following format:

    SERVER=[netsblox server ip]
    PORT=[anki-vector RPC port]
    KEYMODE=[int or binary (optional, default is int)]

Run `__main__.py` and the program will attempt to connect to all robots in `.robots` and relay commands sent by the NetsBlox server.

The KEYMODE environment variable controls how the "hardware key" is displayed. For educational purposes, there are options to display it both as numeric values and as binary strings.