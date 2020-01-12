CC := gcc
LIBS=gio-2.0
CFLAGS=-O0 -ggdb3 `pkg-config --cflags $(LIBS)`
LDFLAGS=`pkg-config --libs $(LIBS)`

.PHONY: clean
default: gdbus-example
gdbus-example: gdbus-example.o
	$(CC) $^ $(LDFLAGS) -o $@

%.o: %.c
	$(CC) $(INCLUDE) $(CFLAGS) -o $@ -c $^

clean:
	rm -f *.o gdbus-example
