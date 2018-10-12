# opendlv-microservices-monitor

Microservice to oversee the resource consumption of other docker microservices running on the platform. 

It publishes to a [OpenDaVINCI](https://github.com/se-research/OpenDaVINCI)/[libcluon](https://github.com/chrberger/libcluon) conference information on containers' CPU usage in percentage value, memory usage in bytes (total memory and Resident Set Size), memory usage in percentage value with respect to the total memory available to the microservice, and the number of CPU cores available. 

The data is contained in the [opendlv message](https://github.com/chalmers-revere/opendlv.standard-message-set) `opendlv.system.MicroserviceStatistics`.

---

Usage: `microservices-monitor.py [--cid=<X>] [-v, --verbose] [-d, --debug]`

Options

`--cid=<X>`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the CID to which publish data. Default 111.

`-v, --verbose`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display info in console.

`-d, --debug`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display info and docker API result in console.

---
Run with 

`docker run --rm -ti --init --net=host -v /var/run/docker.sock:/var/run/docker.sock opendlv-microservices-monitor[:tag] [options]`
