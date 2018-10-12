#!/usr/bin/env python2

# Copyright (C) 2018 Christian Berger
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Author: Federico Giaimo

# OD4Session is needed to send and receive messages
import OD4Session
# Import the OpenDLV Standard Message Set.
import opendlv_standard_message_set_v0_9_8_pb2 as opendlv_messages

import sys
import getopt
import traceback
import docker
import time
import datetime

def exception_handling(verbose):
    if verbose:
        traceback.print_exc()
        sys.exc_clear()

def main(argv):
    # Default CID if not provided via command line options
    cid=111
    verbose=False
    debug=False
    try:
        opts, args = getopt.getopt(argv,"vd",["cid=","verbose","debug"])
    except getopt.GetoptError, err:
        print err.msg
        print "Usage: microservices-monitor.py [--cid=<X>] [-v, --verbose] [-d, --debug]"
        print "Options:"
        print "\t--cid=<X>\tSpecify the CID to which publish data. Default 111."
        print "\t-v, --verbose\tDisplay info in console."
        print "\t-d, --debug\tDisplay info and docker API result in console."
        return 1

    # Parsing options
    for opt, arg in opts:
        if opt in ("--cid"):
            cid = arg
        elif opt in ("-v","--verbose"):
            verbose=True 
        elif opt in ("-d","--debug"):
            verbose = True
            debug = True
    
    if verbose:
        print "\n--- Microservices Monitor ---\n"

    # Create a session to send and receive messages from a running OD4Session;
    session = OD4Session.OD4Session(int(cid))
    # Connect to the network session.
    session.connect()

    # Create a docker client from environmental variables
    dockerClient = docker.from_env()

    ################################################################################

    while True:
        timeBegin = time.time()
        if verbose:
            print "\n["+datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+"]"

        microserviceStats = opendlv_messages.opendlv_system_MicroserviceStatistics()
        critical_fail = False

        try:
            containersList = dockerClient.containers.list(all=True)
        except Exception:
            exception_handling(verbose)
            print "Failure to retrieve containers from docker client!"
            critical_fail = True
            break

        for container in containersList:
            containerName = '{{0: <{}}}'.format(25).format(container.name) + " ["+container.id[0:12]+"] "
            try:
                stats = container.stats(stream=False)
            except Exception:
                exception_handling(verbose)
                print "Failure to retrieve statistics from containers!"
                critical_fail = True
                break

            if debug:
                print stats

            prev_total_usage = 0
            prev_system_cpu_usage = 0
            total_usage = 0
            system_cpu_usage = 0
            num_cores = 0
            try:
                # Get previous cpu usage
                prev_total_usage = float(stats['precpu_stats']['cpu_usage']['total_usage'])
                prev_system_cpu_usage = float(stats['precpu_stats']['system_cpu_usage'])
                # Get current cpu usage
                total_usage = float(stats['cpu_stats']['cpu_usage']['total_usage'])
                system_cpu_usage = float(stats['cpu_stats']['system_cpu_usage'])
                # Get number of cores
                num_cores = int(stats['cpu_stats']['online_cpus'])
            except Exception:
                exception_handling(verbose)

            VIRT = 0
            mem_limit = 0
            RES = 0
            try:
                # Get memory usage
                VIRT = int(stats['memory_stats']['usage'])
                # Get memory usage limit
                mem_limit = int(stats['memory_stats']['limit'])
                # Get resident set size
                RES = int(stats['memory_stats']['stats']['rss'])
            except Exception:
                exception_handling(verbose)

            # Compute container cpu usage delta
            cpuDelta = total_usage - prev_total_usage
            # Compute system cpu usage delta
            sysDelta = system_cpu_usage - prev_system_cpu_usage
            # Initialization of percentage variables
            cpuPercent = 0.0
            memPercent = 0.0
            # Division by 0 checks
            if sysDelta > 0.0 and cpuDelta > 0.0 :
                cpuPercent = (cpuDelta / sysDelta) * 100.0
            if mem_limit > 0.0 :
                memPercent = (float(VIRT) / mem_limit) * 100.0

            # Prepare OD4 session data structures
            microserviceStats.name = container.name
            microserviceStats.identifier = container.id
            microserviceStats.cores = num_cores
            microserviceStats.CPU = cpuPercent
            microserviceStats.VIRT = VIRT
            microserviceStats.RES = RES
            microserviceStats.MEM = memPercent

            if verbose:
                print "*******************************************"
                print "** MS name:    : " + microserviceStats.name
                print "** MS ID:      : " + microserviceStats.identifier
                print "** MS cores (#): " + str(microserviceStats.cores)
                print "** MS CPU   (%): " + str('%.3f'%(microserviceStats.CPU))
                print "** MS VIRT  (B): " + str(microserviceStats.VIRT)
                print "** MS RES   (B): " + str(microserviceStats.RES)
                print "** MS MEM   (%): " + str('%.3f'%(microserviceStats.MEM))
                print "*******************************************"

            session.send(1105, microserviceStats.SerializeToString());

        if critical_fail:
            break

        if verbose:
            print "CID: "+str(cid)+" Elapsed time: "+str('%.2f'%(time.time()-timeBegin))+"s"

    if critical_fail:
        print "Critical failure, exiting..."
        return 1

        ############################################################################


if __name__ == "__main__":
   main(sys.argv[1:])

