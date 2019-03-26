#!/usr/bin/env python3
"""Script to measure delay and losses and tweet them to ISP."""
import csv
import time
import subprocess
import argparse
import matplotlib.pyplot as plt
import numpy as np
import tweepy


def ping(path_to_csv, test_duration):
    """Log delay and losses of ping."""
    hostname = "8.8.8.8"  # Google DNS
    cmd = ["ping", "-W", "1", "-c", "1", hostname]
    counter = 0
    duration_seconds = test_duration*60*60
    elapsed_time = 0
    with open(path_to_csv, "w") as f:
        row_writer = csv.writer(
            f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Run it for a day
        print("Pinging started!")
        while elapsed_time < duration_seconds:

            start = time.time()
            # Fetch the output from the built in ping
            output = subprocess.Popen(
                cmd, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
            output = output.splitlines()
            loss = 0
            delay = 0
            # Parse the ping output
            for out in output:
                if "packet loss" in out:
                    if "100.0%" in out:
                        loss = 100
                        delay = 1000
                        break
                if "round-trip" in out:
                    out = out.split("/")
                    for o in out:
                        try:
                            delay = float(o)
                        except:
                            pass
            elapsed_time = counter * 5
            # Write csv file
            row_writer.writerow([elapsed_time, delay, loss])
            counter += 1
            # MEasure how long the process took
            end = time.time() - start
            # Ensure that each run in the loop takes 5 seconds
            sleep_time = 5 - end
            time.sleep(sleep_time)


def plot_csv(path_to_csv, path_to_plot):
    """Make a plot of a csv."""
    data = np.genfromtxt(path_to_csv, delimiter=',',
                         names=['time', 'delay', 'loss'])

    plt.title("Loss and Delay over a day")
    plt.xlabel("Time")
    plt.ylabel("Delay/loss ms/%")
    plt.plot(data['time'], data['delay'], color='g', label='Delay')
    plt.plot(data['time'], data['loss'], color='b', label='Loss')
    plt.legend()

    plt.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)

    plt.savefig(path_to_plot)

def get_stats(path_to_csv):
    """Function to calculate statitics."""
    data = np.genfromtxt(path_to_csv, delimiter=',',
                         names=['time', 'delay', 'loss'])

    delay_number = sum(i > 80 for i in data["delay"])
    loss_number = sum(i > 0 for i in data["loss"])

    delay_percent = (delay_number / len(data["delay"])) * 100
    loss_percent = (loss_number / len(data["loss"])) * 100

    delay_percent = "{0:.2f}".format(delay_percent)
    loss_percent = "{0:.2f}".format(loss_percent)

    return delay_percent, loss_percent


def post_to_twitter(isp_name, path_to_plot, delay_percent, loss_percent):
    """Posts a comment and picture to the ISP."""
    
    consumer_key = ""
    consumer_secret = ""
    access_token_key = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth)
    message = ("Hi {}, yesterday the internet I have from you was down "
               "{}% of the day and {}% of the day the I suffered from delays higher "
               "then 80ms when pinging google.com".format(isp_name,
                                                          loss_percent,
                                                          delay_percent))
    api.update_with_media(path_to_plot, status=message)

def argsparser():
    parser = argparse.ArgumentParser(description='Check delay and packetloss of '
                                                 'your connection.')
    parser.add_argument('--twitter-name', metavar='n', type=str,
                        help='Twitter name of your ISP')
    parser.add_argument('--duration', metavar='d', type=int,
                        help='How many hours the test should run')
    return parser.parse_args()
    

def main(twitter_name, test_duration):
    """Main function."""
    # Fist create ping data
    path_to_csv = "ping_log.csv"
    ping(path_to_csv, test_duration)
    # Then create the plot
    path_to_plot = "plot.png"
    plot_csv(path_to_csv, path_to_plot)
    # Get some numbers on how bad your connection really is
    delay_percent, loss_percent = get_stats(path_to_csv)
    # Post it on twitter if the connection is bad!
    if float(delay_percent) > 1 or float(loss_percent) > 3:
        path_to_plot = "plot.png"
        post_to_twitter(twitter_name, path_to_plot, delay_percent, loss_percent)

if __name__ == "__main__":
    args = argsparser()
    main(args.twitter_name, args.duration)
