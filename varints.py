# comes from dowski
# gotta ask him what his copyright is
# modification by Chloe Desoutter <chloe.desoutter@atasta.net>

"""Encode and decode VARINTs in Python

Just wrote this while trying to understand exactly how VARINTs work. Maybe
someone else will find this useful too.

Here's where I was reading about VARINTs:

    https://developers.google.com/protocol-buffers/docs/encoding

"""


def encode_varint(value):
    """Encodes a single Python integer to a VARINT."""
    return "".join(encode_varint_stream([value]))


def decode_varint(value):
    """Decodes a single Python integer from a VARINT.

    Note that `value` may be a stream containing more than a single
    encoded VARINT. Only the first VARINT will be decoded and returned. If
    you expect to be handling multiple VARINTs in a stream you might want to
    use the `decode_varint_stream` function directly.

    """
    return decode_varint_stream(value).next()

def varint_length(value):
    length = 0
    while True:
        length += 1
        if value > 127:
            value >>= 7
        else:
            break
    return length

def encode_varint_stream(values):
    """Lazily encodes an iterable of Python integers to a VARINT stream."""
    for value in values:
        while True:
            if value > 127:
                # Yield a byte with the most-significant-bit (MSB) set plus 7
                # bits of data from the value.
                yield chr((1 << 7) | (value & 0x7f))

                # Shift to the right 7 bits to drop the data we've already
                # encoded. If we've encoded all the data for this value, set the
                # None flag.
                value >>=  7
            else:
                # This is either the last byte or only byte for the value, so
                # we don't set the MSB.
                yield chr(value)
                break


def decode_varint_stream(stream):
    """Lazily decodes a stream of VARINTs to Python integers."""
    value = 0
    base = 1
    for raw_byte in stream:
        val_byte = ord(raw_byte)
        value += (val_byte & 0x7f) * base
        if (val_byte & 0x80):
            # The MSB was set; increase the base and iterate again, continuing
            # to calculate the value.
            base *= 128
        else:
            # The MSB was not set; this was the last byte in the value.
            yield value
            value = 0
            base = 1
