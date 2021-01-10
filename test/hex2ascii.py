# Encoding Decoding Hex Bytes
data = 'START\r\n {"value": 34, "person": "john doe"}  # €\r\nEND'
hex_data = ' '.join(hex(ord(n)) for n in data)
print(hex_data)
hex_arr = hex_data.split(' ')
hex_str = ''.join(chr(int(n, 16)) for n in hex_arr)
print(hex_arr)
for n in hex_arr:
    print(int(n, 16), " --> ", chr(int(n, 16)))
print(hex_str)
print('\\n', '\n')
print('chr(10)', chr(10))
print('chr(0xa)', chr(0xa))
