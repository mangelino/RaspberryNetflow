# Introduction

The RaspberryPi Netflow demo is used to demonstrate the capabilities of MediationZone on small devices, 
such as the RasperryPi.

The demo consists of a RasperryPi configured as a WiFi Access Point, which records the activity
of the devices connected to the AP. This activity is collected via Netflow v5 protocol (Netwlow extension for IPtables) 
by a MZ workflow. 

The collected data is aggregated by source and destination address by counting the used volume and number
of packets. The current aggregated values are output every 30 sec.

The output data is enriched by performing a lookup to ARIN to determine the owner of the IP address range.
The ARIN results are cached locally to avoid unnecessary lookups.

Finally the enriched records are transformed in JSON and published via a WebSocket agent. A simple web page
connects via JavaScript to the web socket and displays the data via a Chord diagram (using D3.js).

## Usage

In order to use the demo, simply plug in the Raspberry Pi to a power outlet and connect the Ehternet interface
in order to have Internet access (it should work also for connections requiring authentication, even if it has not been tested).

Once started, an AP named Pi3-AP will appear in the WiFi AP list. Connect to it and enter `raspberry` as password.

Now your device (laptop, phone, tablet) should be able to access the Internet via the RaspberryPi and all traffic will
be captured by the device. 

By pointing a browser to the following address http://192.168.120.1/ you should get a page displaying a diagram representing the different
IP connections known by the RaspberryPi. 

## Diagram
The chord diagram represents data reletionships thank to chords. An IP flow is modeled by a relation *`Source->Destination [Volume]`*.
Source and Destination will be represented as a sector on the outer edge of the diagram, and visualized as the corresponding IP address,
together with the owner organization name, if the space allows.
The bidirectional data flow between two addresses is represented by a chord. The chord has a color related to endpoint from which data was downloaded
from the RasperryPi local network point of view. The size of the chord at each endpoint represents the volume of data sent by that endpoint to the other.

This means that a device connected to the RaspberryPi AP, and accessing Youtube, will be considered as _downloading_ data from Youtube (video data),
as well as uploading data to Youtube (eg. a REST API post, or the content of a HTTP GET). The chord will likely show thinner on the local device end, 
and fatter on the Youtube server end.

# Creating the Raspberry image from scratch

You need:
* A RaspberryPi model 3
* An SD Card with at least 8GB (16GB recommended)
* A computer and an ethernet cable
* (optional) screen, HDMI cable, mouse, keyboard

## Getting the base image
Start by donwloading the official [Rasbpian image](https://downloads.raspberrypi.org/raspbian_lite_latest) from the RaspberryPi website, and follow
the [installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) depending on your OS.

Install the SD card in the RaspberryPi and connect the Pi to the same network to which your computer is connected via the Ethernet cable. Altenatively, you
can connect the Pi to a screen, keyboard and mouse to proceed.

## Fix the DNS resolver

Install `resolvconf`, this is needed to ensure that DNS resolution works.

```
$ sudo apt-get install resolvconf
```

## Install iptables and netflow module

Time to install the [netflow module](https://github.com/aabc/ipt-netflow) for IPtables.
```
$ git clone git://github.com/aabc/ipt-netflow.git ipt-netflow
$ cd ipt-netflow
$ apt-get install module-assistant
$ m-a prepare
$ apt-get install iptables-dev pkg-config
...
~/ipt-netflow$ ./configure
~/ipt-netflow$ make all install
~/ipt-netflow$ depmod
```
Add the following options in `/etc/modprobe.d/ipt_NETFLOW.conf`
    
    protocol=5
    natevents=1

Now enable netflow
```
$ modprobe ipt_NETFLOW destination=127.0.0.1:2055
$ iptables -I FORWARD - j NETFLOW
$ iptables -I INPUT -j NETFLOW
$ iptables -I OUTPUT -j NETFLOW
```
From now on, netflow records will be generated for all traffic transiting via the Pi.

## Install Mediation Zone

Obtain the MZ installation pack. You can generate a new installer by using the [following](https://artifactory.digitalroute.com/artifactory/deliveries/7.3.1.0/DR_RaspberryPi_derby_20160928_113200_20160929-170758/DR_RaspberryPi_derby_20160928_113200_20160929-170758.pdf) SDR from Artifactory. 
Keep in mind that the Pi does not have much memory, and the SD card is not super fast storage: limit the number of features to the minimum.

Once you got the `mzp`, copy it to the Pi, and follow the normal MZ installation instructions. You can create an `mzadmin` user or you can cuse the existing `pi` user.
> **Note:** you can use `scp pi@raspberry.local` to copy the files to the Pi without needing to know the Pi address, since the Pi uses mDNS. 

## Configure `common.xml`

In MZ7.3 and below, running the `mzsh` command always trigger a safe copy of the content of the `CLASSPATH`. Given that the SD card used in the Pi is not really fast, 
this means that any command takes several seconds to execute. In order speed things up, you can simply add the followinf property to the `$MZ_HOME/etc/common.xml` files

    <property name="mz.picosync.classpath.copy" value="false"/>



