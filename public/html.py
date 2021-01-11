#!/usr/bin/env python3
import os

# Turn on debug mode.
import cgitb
cgitb.enable()


# Begin HTML generation
print("Content-Type: text/html; charset=UTF-8")  # Print headers
print("")
content = """    
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>The HTML5 GSM</title>
  <meta name="description" content="The HTML5 GSM">
  <meta name="author" content="GSM">

</head>

<body>
  <h1>OK....</h1> 
  <p>{}</p> 
</body>
</html>
"""
type = os.environ.get("QUERY_STRING").split("&")
get = dict()
if len(type) > 0:
    for t in type:
        values = t.split("=")
        if len(values) == 2:
            get[values[0]] = values[1]

val = get
if len(get) == 0:
    val = os.environ

print(content.format(val))
