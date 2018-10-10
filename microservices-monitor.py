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
import opendlv_standard_message_set_v0_9_7_pb2 as opendlv_messages

import sys
import getopt
import traceback
import docker
import time
import datetime

def main(argv):

    cid=253
    try:
        opts, args = getopt.getopt(argv,"",["cid="])
    except getopt.GetoptError:
        None
    for opt, arg in opts:
        if opt in ("--cid"):
            cid = arg

    print "\n--- Performance Monitor ---\n"
    # Create a session to send and receive messages from a running OD4Session;
    session = OD4Session.OD4Session(int(cid))
    # Connect to the network session.
    session.connect()

    print "Create a docker client\n"
    # Create a docker client from environmental variables. Alternatively it is possible to instantiate a DockerClient object
    dockerClient = docker.from_env()

            #{u'blkio_stats': {u'io_service_time_recursive': [], u'sectors_recursive': [], u'io_service_bytes_recursive': [], u'io_serviced_recursive': [], u'io_time_recursive': [], u'io_queue_recursive': [], u'io_merged_recursive': [], u'io_wait_time_recursive': []}, u'precpu_stats': {u'cpu_usage': {u'usage_in_usermode': 150000000, u'total_usage': 198315991, u'percpu_usage': [6633313, 156385904, 28161932, 7134842], u'usage_in_kernelmode': 40000000}, u'system_cpu_usage': 6733590000000, u'online_cpus': 4, u'throttling_data': {u'throttled_time': 0, u'periods': 0, u'throttled_periods': 0}}, u'name': u'/jovial_heisenberg', u'read': u'2018-08-30T06:21:12.333305582Z', u'storage_stats': {}, u'num_procs': 0, u'preread': u'2018-08-30T06:21:11.33100547Z', u'memory_stats': {u'usage': 22163456, u'limit': 16724475904, u'stats': {u'unevictable': 0, u'total_inactive_file': 69632, u'total_rss_huge': 0, u'hierarchical_memsw_limit': 0, u'total_cache': 69632, u'total_mapped_file': 0, u'mapped_file': 0, u'pgfault': 9261, u'total_writeback': 0, u'hierarchical_memory_limit': 9223372036854771712, u'total_active_file': 0, u'rss_huge': 0, u'cache': 69632, u'active_anon': 19009536, u'pgmajfault': 0, u'total_pgpgout': 2850, u'writeback': 0, u'pgpgout': 2850, u'total_active_anon': 19009536, u'total_unevictable': 0, u'total_pgfault': 9261, u'total_pgmajfault': 0, u'total_inactive_anon': 0, u'inactive_file': 69632, u'pgpgin': 7508, u'total_dirty': 69632, u'total_pgpgin': 7508, u'rss': 19009536, u'active_file': 0, u'inactive_anon': 0, u'dirty': 69632, u'total_rss': 19009536}, u'max_usage': 22597632}, u'pids_stats': {u'current': 3}, u'id': u'f6c85268d339334e52ec54162cc38aaadf92f17a8d122e33d2d902f68d7a1272', u'cpu_stats': {u'cpu_usage': {u'usage_in_usermode': 150000000, u'total_usage': 198342463, u'percpu_usage': [6659785, 156385904, 28161932, 7134842], u'usage_in_kernelmode': 40000000}, u'system_cpu_usage': 6737570000000, u'online_cpus': 4, u'throttling_data': {u'throttled_time': 0, u'periods': 0, u'throttled_periods': 0}}}

    ################################################################################

    while True:
        timeBegin = time.time()
        print "\n["+datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+"]"
        
        microserviceStats = opendlv_messages.opendlv_system_MicroserviceStatistics()

        containersList = dockerClient.containers.list(all=True)

        for container in containersList:
            containerName = '{{0: <{}}}'.format(25).format(container.name) + " ["+container.id[0:12]+"] "

            try:
                stats = container.stats(stream=False)

                # Get previous cpu usage
                prev_total_usage = float(stats['precpu_stats']['cpu_usage']['total_usage'])
                prev_system_cpu_usage = float(stats['precpu_stats']['system_cpu_usage'])

                # Get current cpu usage
                total_usage = float(stats['cpu_stats']['cpu_usage']['total_usage'])
                system_cpu_usage = float(stats['cpu_stats']['system_cpu_usage'])

                # Get number of cores
                num_cores = int(stats['cpu_stats']['online_cpus'])

                VIRT = int(stats['memory_stats']['usage'])
                mem_limit = int(stats['memory_stats']['limit'])
                RES = int(stats['memory_stats']['stats']['rss'])

            except KeyError, e:
                print "*******************************************"
                print "KeyError exception on key "+str(e)+" while probing container "+containerName
                print "-------------------------------------------"
                print "Traceback: "
                traceback.print_exc()
                sys.exc_clear()
                print "*******************************************"
                continue
            except Exception, e:
                print "*******************************************"
                print "Exception: "+str(e)+" while probing container "+containerName
                print "-------------------------------------------"
                print "Traceback: "
                traceback.print_exc()
                sys.exc_clear()
                print "*******************************************"
                continue

            # Compute container cpu usage delta
            cpuDelta = total_usage - prev_total_usage
            # Compute system cpu usage delta
            sysDelta = system_cpu_usage - prev_system_cpu_usage
            cpuPercent = 0.0
            if sysDelta > 0.0 and cpuDelta > 0.0 :
                cpuPercent = (cpuDelta / sysDelta) * 100.0
            memPercent = (float(VIRT) / mem_limit) * 100.0

            # Prepare OD4 session data structures
            microserviceStats.name = container.name
            microserviceStats.identifier = container.id
            microserviceStats.cores = num_cores
            microserviceStats.CPU = cpuPercent
            microserviceStats.VIRT = VIRT
            microserviceStats.RES = RES
            microserviceStats.MEM = memPercent

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

        print "CID: "+str(cid)+" Elapsed time: "+str('%.2f'%(time.time()-timeBegin))+"s"

        ############################################################################


if __name__ == "__main__":
   main(sys.argv[1:])

