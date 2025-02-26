#!/usr/bin/env python3

import sys,os,glob,uuid
import subprocess as sub
import argparse as ap

def main(args):
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input',   nargs='+', help='Input file pattern (or a list of patterns).', required=True)
    parser.add_argument('-o', '--output', type=str, default='master.log')

    args = vars(parser.parse_args())
    input_patterns = args['input']
    inputs = []
    for ptrn in input_patterns:
        inputs += glob.glob(ptrn,recursive=True)

    nfiles = len(inputs)
    print('Inputs:')
    for infile in inputs:print('\t{}'.format(infile))

    outdirs = ['tmp_{}_{}'.format(uuid.uuid4(),uuid.uuid4()) for i in range(nfiles)]

    delete_files = []

    for i in range(nfiles):
        # unpack the tar file
        comm = 'mkdir {a} && tar xf {b} -C {a} --strip-components 1'.format(a=outdirs[i],b=inputs[i])
        sub.check_call(comm,shell=True)

    # Combine all of the payload log files.
    comm = 'cat tmp_*_*/payload.stdout > {}'.format(args['output'])
    sub.check_call(comm,shell=True)
   
    # Delete the unpacked tars.
    comm = ['rm','-r']
    for outdir in outdirs: comm += [outdir]
    sub.check_call(comm)
    return

if __name__ == '__main__':
    main(sys.argv)
