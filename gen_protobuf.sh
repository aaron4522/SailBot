#!/bin/sh

cd protobuf
protoc -omessages.pb messages.proto
python nanopb/generator/nanopb_generator.py messages.pb
cp messages.pb.h messages.pb.c ../controller/LoRaController
cp messages.pb.h messages.pb.c ../controller/LoRaReceiver
