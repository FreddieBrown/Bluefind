# CC := gcc
# CFLAGS := -std=c99 `pkg-config --cflags --libs gio-2.0 dbus-1 glib-2.0` -lbluetooth
# TARGET := main

# SRCDIR := src
# OBJDIR := obj

# SRC := ${wildcard ${SRCDIR}/*.c}
# OBJ := ${SRC:${SRCDIR}/%.c=${OBJDIR}/%.o}

# default: build

# debug: CFLAGS += -g
# debug: build

# build: ${OBJ}
# 	${CC} -o ${TARGET} ${OBJ} ${CFLAGS}

# ${OBJDIR}/%.o: ${SRCDIR}/%.c
# 	$(CC) $(CFLAGS) -c $< -o $@

# .PHONY: clean

# clean:
# 	rm -f ${OBJDIR}/*.o ${TARGET}


CXX=g++
CFLAGS= -g -O3 `pkg-config --cflags --libs gio-2.0 dbus-1 glib-2.0` \
       -Wno-unused-function -Wno-unknown-warning-option -o bluefind


build: src/*.cpp
		$(CXX) src/*.cpp $(CFLAGS) -o bluefind

clean:
		rm -rf bluefind