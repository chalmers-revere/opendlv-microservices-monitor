all: cluonDataStructures_pb2.py opendlv_standard_message_set_v0_9_7_pb2.py

cluonDataStructures.proto: cluonDataStructures.odvd
	cluon-msc --proto --out=cluonDataStructures.proto cluonDataStructures.odvd

cluonDataStructures_pb2.py: cluonDataStructures.proto
	protoc --python_out=. cluonDataStructures.proto

opendlv_standard_message_set_v0_9_7.proto: opendlv-standard-message-set-v0.9.7.odvd
	cluon-msc --proto --out=opendlv_standard_message_set_v0_9_7.proto opendlv-standard-message-set-v0.9.7.odvd

opendlv_standard_message_set_v0_9_7_pb2.py: opendlv_standard_message_set_v0_9_7.proto
	protoc --python_out=. opendlv_standard_message_set_v0_9_7.proto

clean:
	rm -f *_pb2.py *pyc *.proto 
