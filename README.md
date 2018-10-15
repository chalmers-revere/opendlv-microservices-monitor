# opendlv-microservices-monitor

Microservice to oversee the resource consumption of other docker microservices running on the platform. 

It publishes to a [OpenDaVINCI](https://github.com/se-research/OpenDaVINCI)/[libcluon](https://github.com/chrberger/libcluon) conference information on containers' CPU usage in percentage value, memory usage in bytes (total memory and Resident Set Size), memory usage in percentage value with respect to the total memory available to the microservice, and the number of CPU cores available. 

The data is contained in the [opendlv message](https://github.com/chalmers-revere/opendlv.standard-message-set) `opendlv.system.MicroserviceStatistics`.

---
## Dependencies

* [libcluon](https://github.com/chrberger/libcluon) - [![License: GPLv3](https://img.shields.io/badge/license-GPL--3-blue.svg
)](https://www.gnu.org/licenses/gpl-3.0.txt) is necessary to interprete the output messages.

---

## Usage

This microservice is created automatically on changes to this repository via Docker's public registry for:
* [x86_64](https://hub.docker.com/r/chalmersrevere/opendlv-microservices-monitor-amd64/tags/)
* [armhf](https://hub.docker.com/r/chalmersrevere/opendlv-microservices-monitor-armhf/tags/)
* [aarch64](https://hub.docker.com/r/chalmersrevere/opendlv-microservices-monitor-aarch64/tags/)

To run this microservice using our pre-built Docker multi-arch images, start it as follows:

`docker run --rm -ti --init --net=host -v /var/run/docker.sock:/var/run/docker.sock opendlv-microservices-monitor[:tag] [options]`

### Usage message:

Usage: `microservices-monitor.py [--cid=<X>] [-v, --verbose] [-d, --debug]`

Options

`--cid=<X>`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the CID to which publish data. Default 111.

`-v, --verbose`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display info in console.

`-d, --debug`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display info and docker API result in console.

---
## License

* This project is released under the terms of the GNU GPLv3 License
