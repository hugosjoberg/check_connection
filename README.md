# Check connection

This project is used to ping google's DNS 8.8.8.8 during server. The packet loss and delay are measured. A graph of the results is then created and if during the test time we had a 100% packet loss (Internet down!) during more then 3% of the test duration or a delay higher then 80ms during 1% of the test, a message is sent to the ISP you have specified on twitter.

## Getting Started

I recommend that you run this test on a raspberry pi connected by wire to your router/modem to ensure that the problem is with your internet connection and not your wireless connection.

### Prerequisites

If the test is running on a raspberry pi running raspbian the following python packages needs to be installed:

```
python3 -m pip install matplotlib
python3 -m pip install numpy
python3 -m pip install tweepy
```

### Installing and running

Clone this repo to your unit. Run the following command to ensure the python file is executable:

```chmod +x check_connection.py```

Run the program by calling 

```./check_connection.py --twitter-name <unknown> --duration 1```

Replace `<unknown>` with your ISP's twitter name and `1` with the number of hours you want the test to run.


## License

This project is licensed under the MIT License.
