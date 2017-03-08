#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
	"A Node with IP forwarding enabled."

	def config( self, **params ):
		super( LinuxRouter, self).config( **params )
		# Enable forwarding on the router
		self.cmd( 'sysctl net.ipv4.ip_forward=1' )

	def terminate( self ):
		self.cmd( 'sysctl net.ipv4.ip_forward=0' )
		super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):
	"A LinuxRouter"

	def build( self, **_opts ):
		defaultIP1 = '10.1.0.1/24'  # IP address for r1-eth1
		router1 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP1 )

		defaultIP2 = '10.1.1.129/26'  # IP address for r2-eth1
		router2 = self.addNode( 'r2', cls=LinuxRouter, ip=defaultIP2 )

                defaultIP3 = '8.8.8.8/24'  # IP address for r3-eth1
		router3 = self.addNode( 'r3', cls=LinuxRouter, ip=defaultIP3 )

        #250 pc
		h1 = self.addHost( 'h1', ip='10.1.0.2/24', defaultRoute='via 10.1.0.1' )
		h2 = self.addHost( 'h2', ip='10.1.0.2/24', defaultRoute='via 10.1.0.1' )
		#125 pc
		h3 = self.addHost( 'h3', ip='10.1.1.2/25', defaultRoute='via 10.1.1.1' )
		h4 = self.addHost( 'h4', ip='10.1.1.2/25', defaultRoute='via 10.1.1.1' )
		#60 pc
		h5 = self.addHost( 'h5', ip='10.1.1.130/26', defaultRoute='via 10.1.1.129' )
		h6 = self.addHost( 'h6', ip='10.1.1.130/26', defaultRoute='via 10.1.1.129' )
		#2 pc (CEO)
		h7 = self.addHost( 'h7', ip='10.1.1.194/29', defaultRoute='via 10.1.1.193' )
		h8 = self.addHost( 'h8', ip='10.1.1.194/29', defaultRoute='via 10.1.1.193' )
		#2 pc (net admin)
		h9 = self.addHost( 'h9', ip='10.1.1.202/29', defaultRoute='via 10.1.1.201' )
		h10 = self.addHost( 'h10', ip='10.1.1.202/29', defaultRoute='via 10.1.1.201' )
		
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')
		s4 = self.addSwitch('s4')
		s5 = self.addSwitch('s5')
		#switch to connect r3  router with the isp server
		s6 = self.addSwitch('s6')

		#link between switches and hosts
		self.addLink(h1, s1)
		self.addLink(h2, s1)
		self.addLink(h3, s2)
		self.addLink(h4, s2)
		self.addLink(h5, s3)
		self.addLink(h6, s3)
		self.addLink(h7, s4)
		self.addLink(h8, s4)
		self.addLink(h9, s5)
		self.addLink(h10, s5)

		#router1 interfaces
		self.addLink( s1, router1, intfName2='r1-eth1', params2={ 'ip' : '10.1.0.1/24' } )
		self.addLink( s2, router1, intfName2='r1-eth2', params2={ 'ip' : '10.1.1.1/25' } )

		#router2 interfaces
		self.addLink( s3, router2, intfName2='r2-eth1', params2={ 'ip' : '10.1.1.129/26' } )
		self.addLink( s4, router2, intfName2='r2-eth2', params2={ 'ip' : '10.1.1.193/29' } )
		self.addLink( s5, router2, intfName2='r2-eth3', params2={ 'ip' : '10.1.1.201/29' } )

		#router3 interfaces
		self.addLink( s6, router2, intfName2='r3-eth1', params2={ 'ip' : '8.8.8.8/24' } )
                
		#serial link between two routers(r1, r2)
		self.addLink( router1, router2, intfName1='r1-eth3', params1={ 'ip' : '10.1.1.209/30' }, intfName2='r2-eth4', params2={ 'ip' : '10.1.1.210/30' } )
		#serial link between two routers(r2, r3)
		self.addLink( router2, router3, intfName1='r2-eth5', params1={ 'ip' : '193.168.200.1/24' }, intfName2='r3-eth2', params2={ 'ip' : '193.168.200.2/24' } )

def run():
	"Test linux router"
	topo = NetworkTopo()
	net = Mininet( topo=topo )
	net.start()

	# IMPORTANT: IP routing between different networks doesn't work if we don't make these routing table entries.
        #the packets to be send to the r2 by r1
	net[ 'r1' ].cmd( 'ip route add 10.1.1.128/26 via 10.1.1.210' )
	net[ 'r1' ].cmd( 'ip route add 10.1.1.192/29 via 10.1.1.210' )
	net[ 'r1' ].cmd( 'ip route add 10.1.1.200/29 via 10.1.1.210' )
        #the packets to be send to the r1 by r2
        net[ 'r2' ].cmd( 'ip route add 10.1.0.0/24 via 10.1.1.209' )
        net[ 'r2' ].cmd( 'ip route add 10.1.1.0/25 via 10.1.1.209' )
        ##the packets to be send to the r3 by r2
        net[ 'r2' ].cmd( 'ip route add 0.0.0.0/0 via 193.168.200.2' )
        ##the packets to be send to the r2 by r3
        net[ 'r3' ].cmd( 'ip route add 10.1.1.128/26 via 193.168.200.1' )
        net[ 'r3' ].cmd( 'ip route add 10.1.1.192/29 via 193.168.200.1' )
        net[ 'r3' ].cmd( 'ip route add 10.1.1.200/29 via 193.168.200.1' )


	info( '*** Routing Table on Router1:\n' )
	print net[ 'r1' ].cmd( 'route' )

	info( '*** Routing Table on Router2:\n' )
	print net[ 'r2' ].cmd( 'route' )
	
	info( '*** Routing Table on Router3:\n' )
	print net[ 'r3' ].cmd( 'route' )

	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	run()

