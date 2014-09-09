#!/usr/bin/python2
# Licensed under the Revised MIT license
# (c) 2014 Chloe Desoutter, Atasta NET <chloe.desoutter@atasta.net>

import snappy
from varints import *
from struct import *
import resources.messagetypes.Identifier
import itertools
import inspect
# ugly
import sys
sys.path.insert(1, './resources/protobuf')
# for i in resources/protobuf/*py;do echo import $i;done | grep -v __init__ | tr / . | sed 's/.py$//g'
import resources.protobuf.KNArchives_pb2
import resources.protobuf.KNCommandArchives_pb2
import resources.protobuf.TNArchives_pb2
import resources.protobuf.TNCommandArchives_pb2
import resources.protobuf.TPArchives_pb2
import resources.protobuf.TPCommandArchives_pb2
import resources.protobuf.TSAArchives_pb2
import resources.protobuf.TSCEArchives_pb2
import resources.protobuf.TSCH3DArchives_pb2
import resources.protobuf.TSCHArchives_pb2
import resources.protobuf.TSCHCommandArchives_pb2
import resources.protobuf.TSCHPreUFFArchives_pb2
import resources.protobuf.TSDArchives_pb2
import resources.protobuf.TSDCommandArchives_pb2
import resources.protobuf.TSKArchives_pb2
import resources.protobuf.TSPArchiveMessages_pb2
import resources.protobuf.TSPDatabaseMessages_pb2
import resources.protobuf.TSPMessages_pb2
import resources.protobuf.TSSArchives_pb2
import resources.protobuf.TSTArchives_pb2
import resources.protobuf.TSTCommandArchives_pb2
import resources.protobuf.TSTStylePropertyArchiving_pb2
import resources.protobuf.TSWPArchives_pb2
import resources.protobuf.TSWPCommandArchives_pb2

from google.protobuf.message import DecodeError


class PyIWA(object):
  def __init__(self):
    self.finder = resources.messagetypes.Identifier.Identifier()
  def load_stream(self, stream):
    off = 0
    length = len(stream)
    chunkLength = 0x00000000
    streamd = snappy.StreamDecompressor()
    dec = b""
    while (off + 4 < length):
      piece = stream[off:off+4]
      chunkLength = unpack('<BBBB', piece)
      if (chunkLength[0] & 0xFF != 0):
        print u"ooops!"
        return False

      chunkAsInt = unpack('<i', '\0'+piece[1:])[0] >> 8
      if (off + chunkAsInt > length):
        print u"Bad chunk (off: %d cai: %d len: %d)" % (off, chunkAsInt, length)
        return False
      off += 4
      dec += snappy._uncompress(stream[off:off+chunkAsInt])
      off += chunkAsInt

    return dec
    
  def parse_stream(self, stream):
    iwork_file = resources.protobuf.TSPArchiveMessages_pb2.ArchiveInfo()
    iwork_info = resources.protobuf.TSPArchiveMessages_pb2.MessageInfo()

    length = len(stream)

    parsed_stream = []
    all_parsed_items = []
    """ promises it will only decode the first varint, so..."""
    try:
      chunk_len = decode_varint(stream)
    except StopIteration:
      return (parsed_stream, all_parsed_items)
    off = varint_length(chunk_len)
    # we have read the first length chunk
    while (off + chunk_len < length):
      # read the piece of data. head is well positioned already
      chunk = stream[off:off+chunk_len]
      iwork_file.ParseFromString(chunk)
      
      if (iwork_file.message_infos):
        bkl=0
        # we are at the beginning of the messageinfo chunk. let's move next
        # so we prepare to read the next binary block
        off += chunk_len
        parsed_stream.append(iwork_file)
        all_parsed_items.append(iwork_file)
        for info in iwork_file.message_infos:
          # next block we read will be this length
          chunk_len = info.length
          next_possible_types = [i for i in self.finder.find_candidates(info.type)]
          bkl+=1
          if (bkl > 1):
            # not supported, eject
            return False
          parsing_candidates = []
          for postyp in next_possible_types:
            classname = self.finder.to_classname(postyp)
            # use introspection to find the right class
            parsing_candidates = [c for c in self._introspect_and_find_candidates(classname)]
          # we have found candidates so let's get the next chunk
          # the off head is already moved, chunk_len is set, go!
          chunk = stream[off:off+chunk_len]
          parsed_candidates = self._introspect_and_parse(chunk, parsing_candidates)
          # we only want one for this purpose
          if (len(parsed_candidates) > 0):
            data = parsed_candidates[0]
            parsed_stream.append(data)
            all_parsed_items.append(parsed_candidates)
      #we have finished read info streams in the message_infos
      # let's move the offset and start over again
      off += chunk_len
      try:
        chunk_len = decode_varint(stream[off:])
      except StopIteration:
        return (parsed_stream, all_parsed_items)
      # we have read the msginfo length. let's offset the head
      off += varint_length(chunk_len)
    return (parsed_stream, all_parsed_items)

  def _introspect_and_parse(self, chunk, parsing_candidates):
    parsed_candidates = []
    for c in parsing_candidates:
      obj = None
      try:
        obj = c()
        obj.ParseFromString(chunk)
      except DecodeError as d:
        continue
      except UnicodeDecodeError as e:
        continue
      parsed_candidates.append(obj)
    return parsed_candidates

  def _introspect_and_find_candidates(self, classname):
    for module in sys.modules:
      #for name, obj in inspect.getmembers(sys.modules[module], inspect.isclass):
      #  print name
      for cls in [obj for name, obj in inspect.getmembers(sys.modules[module], inspect.isclass) if name==classname]:
        yield cls

if (__name__ == '__main__'):
  import sys
  reload(sys).setdefaultencoding("utf-8")
  import io
  fl = sys.argv[1]
  with io.open(fl, 'rb') as fil:
    c = PyIWA()
    decompressed = c.load_stream(fil.read())
    (parsed_stream, all_parsed_items) = c.parse_stream(decompressed)
    for p in parsed_stream:
      if 'text' in p.__class__.__dict__ and len(p.text) > 0:  
        print "\n".join(p.text)
