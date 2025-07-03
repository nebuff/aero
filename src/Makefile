CC=gcc
CFLAGS=-Wall -lncurses
TARGET=aero

all: $(TARGET)

$(TARGET): aero.c
	$(CC) aero.c -o $(TARGET) $(CFLAGS)

clean:
	rm -f $(TARGET)
