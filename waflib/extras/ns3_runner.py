#!/usr/bin/env python
# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

import waflib
from waflib.Configure import conf
from waflib import Utils,Logs,Errors
from waflib.TaskGen import feature

from subprocess import call
from sys import argv
import os

from waflib import Options

def options (ctx):
    ctx.add_option('--runs', dest='runs', help='list of runs')
    pass

def perform (env):
    if not env.options.scenario:
        Logs.error ("At least one scenario should be specified")
        return 1

    scenarios = env.options.scenario.split (',')
    for scenario in scenarios:
        info = scenario.split ('/')
        if (len (info) != 3):
            Logs.error ("Wrong specification of scenario [%s]. Shoulbe [topology]/[type]" % scenario)
            return 2

        runs = ["1"]
        if env.options.runs:
            runs = env.options.runs.split (',')

        scenario = info[0]
        subtype  = info[1]
        np       = info[2]
        Logs.error ("Running %s / %s" % ( scenario, subtype ))

        opentype = "w"
        if env.options.preserve:
            opentype = "a"

        logfile = open ("output/%s-%s.txt" % ( scenario, subtype ), opentype)

        for run in runs:
            cmdline = [# "openmpirun",
                       # "-np", np,
                       "./build/%s" % scenario,
                       # "--mpi=1",
                       "--run=%s" % run,
                       ]
            if run != runs[0]:
                cmdline += ["header=0"]

            # if subtype == "limits":
            cmdline += ["--limits=1"]

            # if subtype == "pitLimits":
            #     cmdline += ["--pitLimits=1"]

            Logs.error (" ".join (cmdline))

            ret = call (cmdline, stdin=None, stdout=logfile, stderr=None)
            if (ret != 0):
                return (ret)

    return 1

