#!/bin/bash

#reingest.py run experiments/ingest/ego_automation.reingest experiments/ingest/ingest.bes_vfs
reingest.py run experiments/ingest/test.reingest experiments/ingest/ingest.bes_vfs ${1+"$@"}
