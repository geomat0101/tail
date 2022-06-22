#!/bin/env python

import sys


class Tail():

    def __init__ (self, fh, limit=10):
        self.fh = fh
        self.limit = limit

    
    def tail (self):
        if self.fh.fileno() == 0:
            # fh is stdin
            # stdin is not seek()-able, must read forward
            return(''.join(self.fh.readlines()[-self.limit:]).strip())
        
        return self.readlines_backwards()


    def readlines_backwards (self):
        fh = self.fh
        limit = self.limit

        step = 256              # how many chars to read at a time
        size = fh.seek(0,2)     # seek to end, get total buffer size

        # check to see if buffer is newline-terminated
        fh.seek(size-1)
        if fh.read(1) != '\n':
            eol_ptrs = [size]   # eof is implicit eol marker if not already newline-terminated
        else:
            eol_ptrs = []

        # initialize offset to last substring in buffer
        offset = size
        if step > size:
            step = size
        offset -= step  # make sure we have data from the first read(), not starting at end of buffer

        # process each substring from end moving back towards beginning, record position of newlines
        while (len(eol_ptrs) < limit):
            fh.seek(offset)
            substring = fh.read(step)
            for i, char in reversed(list(enumerate(substring))):
                if char == '\n':
                    # found one
                    eol_ptrs.append(offset+i)
            if len(eol_ptrs) > limit:
                # got enough newlines identified for the intended tail line limit
                break

            if offset > 0 and offset < step:
                # approaching beginning of buffer
                # make sure to process remaining bytes 0 <= n < step
                step = offset
                offset = 0
            else:
                if offset == 0:
                    eol_ptrs.append(0)  # beginning of buffer is an implicit line boundary as well

                # middle of buffer somewhere, take another step back
                offset -= step

            if offset < 0:
                # buffer exhausted before line limit reached
                break
        
        if len(eol_ptrs) <= limit:
            # return the whole buffer
            fh.seek(0)
        else:
            # index of limit gets us to start of line we care about
            fh.seek(eol_ptrs[limit])

        return(fh.read().strip())



if __name__ == '__main__':
    limit = 0
    if len(sys.argv) >= 2:
        fname = sys.argv[-1]
    
    if len(sys.argv) == 3:
        limit = sys.argv[1]
        if limit.startswith('-'):
            limit = limit[1:]

    if limit:
        length = int(limit)
        if length < 1:
            raise(ValueError('line count must be a positive number'))
    else:
        length = 10

    if len(sys.argv) == 1 or fname == '-':
        print(Tail(sys.stdin, limit=length).tail())
        sys.exit(0)

    with open(fname) as f:
        print(Tail(f, limit=length).tail())
