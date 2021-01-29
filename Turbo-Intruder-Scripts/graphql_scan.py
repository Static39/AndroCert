import os

output_path = "/path/to/output.txt"

# Deletes the file if it exists. Saves you from having to delete before every scan.
if os.path.exists(output_path):
  os.remove(output_path)

# A list to store discovered words
fields = []


def queueRequests(target, wordlists):
    # Tweek these to meet your needs
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=25,
                           requestsPerConnection=200,
                           pipeline=True
                           )
    engine.start()
    # Load a wordlist
    for word in open("/path/to/wordlist.txt"):
        engine.queue(target.req, word.rstrip())

def handleResponse(req, interesting):

    # Checks if GraphQL offered a suggestion
    field_begin = req.response.find("Did you mean") + 13
    if field_begin > 12:
    
        # Strips out the suggested query/field/etc from the response
        end_index = req.response.find("\\\"", field_begin + 1) + 2
        current_field = req.response[field_begin:end_index]
        
        # If the suggested word has already been seen then ignore
        if current_field not in fields and len(current_field) > 0: 
            fields.append(current_field)
            table.add(req)
            
            # Outputs all captured queries/mutations to a file
            output = open(output_path, "a+")
            output.write(current_field[2:len(current_field) - 2] + "\n")
            output.close()
