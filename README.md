# awscli-completion-server

## Description

A simple TCP server which provides awscli completions.

## Installation

### Prerequisites
- pip

### Installation

From the project's root directory run:

- to install locally for the current user:
```
pip install --user .
```

- to install globally:
```
sudo pip install .
```

## Usage

### Starting the server

```
usage: aws-comp-srv [-h] -a ADDRESS -p PORT [-v] [-l LOG]

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        An IP address for the server to listen on
  -p PORT, --port PORT  A TCP port for the server to listen on
  -v, --verbose
  -l LOG, --log LOG
```

### Protocol description

The server accepts messages which consist of two parts: `Header` and `Payload`

#### Header
4-byte unsigned integer (little-endian) representing the `Payload`'s length

#### Payload

JSON-encoded array:

- First (required) element: a string to complete (e.g. `aws cloud`)
- Second (optional) element: a position in the string to start completion at (an integer)
