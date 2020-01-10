CC := gcc
CFLAGS := -Wall -Wextra -Werror -std=c99 -lbluetooth
TARGET := main

SRCDIR := src
OBJDIR := obj

SRC := ${wildcard ${SRCDIR}/*.c}
OBJ := ${SRC:${SRCDIR}/%.c=${OBJDIR}/%.o}

default: build

debug: CFLAGS += -g
debug: build

build: ${OBJ}
	${CC} -o ${OBJ} ${TARGET} ${CFLAGS}

${OBJDIR}/%.o: ${SRCDIR}/%.c
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -f ${OBJDIR}/*.o ${TARGET}