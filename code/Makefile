CC := gcc
CFLAGS := -std=c99 `pkg-config --cflags --libs glib-2.0` -lbluetooth
CFLAGS+=-I/usr/include/dbus-1.0/
TARGET := main

SRCDIR := src
OBJDIR := obj

SRC := ${wildcard ${SRCDIR}/*.c}
OBJ := ${SRC:${SRCDIR}/%.c=${OBJDIR}/%.o}

default: build

debug: CFLAGS += -g
debug: build

extra: CFLAGS += -Wall -Wextra -Werror
extra: build

build: ${OBJ}
	${CC} -o ${TARGET} ${OBJ} ${CFLAGS}

${OBJDIR}/%.o: ${SRCDIR}/%.c
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -f ${OBJDIR}/*.o ${TARGET}