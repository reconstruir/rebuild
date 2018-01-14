#!/bin/bash

( cd _artifacts && tar cf - * | ( cd ../../artifacts ; tar xf - ) )
