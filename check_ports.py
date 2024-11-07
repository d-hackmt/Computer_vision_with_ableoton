import mido

# List all available output ports
print("Available MIDI Output Ports:")
for port in mido.get_output_names():
    print(port)
