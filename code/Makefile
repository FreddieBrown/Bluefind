CC := g++
CFLAGS := -std=c99 `pkg-config --cflags --libs gio-2.0 dbus-1 glib-2.0`
TARGET := bluefind

SRCDIR := src
OBJDIR := obj

SRC := ${wildcard ${SRCDIR}/*.cpp}
OBJ := ${SRC:${SRCDIR}/%.cpp=${OBJDIR}/%.o}

default: build

debug: CFLAGS += -g
debug: build

build: ${OBJ}
	${CC} -o ${TARGET} ${OBJ} ${CFLAGS}

${OBJDIR}/%.o: ${SRCDIR}/%.cpp
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -f ${OBJDIR}/*.o ${TARGET}


# CXX=g++
# CFLAGS= -g -O3 `pkg-config --cflags --libs gio-2.0 dbus-1 glib-2.0` \
#        -Wno-unused-function


# build: src/*.cpp
# 		$(CXX) src/*.cpp $(CFLAGS) -o bluefind

# clean:
# 		rm -rf bluefind