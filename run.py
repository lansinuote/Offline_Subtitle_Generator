from transcribe import transcribe
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-file','-f')
parser.add_argument('-chunk_duration_sec','-c', type=int, default=120)
parser.add_argument('-one_line_max_length','-l', type=int, default=35)

args = parser.parse_args()

print(args)

transcribe(print,args.file,args.chunk_duration_sec,args.one_line_max_length)