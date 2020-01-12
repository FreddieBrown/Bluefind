CC := gcc
LIBS=gio-2.0
CFLAGS := -O0 -ggdb3 `pkg-config --cflags $(LIBS)`
LDFLAGS := `pkg-config --libs $(LIBS)`
TARGET := main

SRCDIR := src
OBJDIR := obj

SRC := ${wildcard ${SRCDIR}/*.c}
OBJ := ${SRC:${SRCDIR}/%.c=${OBJDIR}/%.o}

default: build

debug: CFLAGS += -g
debug: build

extra: CFLAGS +=  -Wall -Wextra -Werror
extra: build

build: ${OBJ}
	${CC} ${OBJ} ${CFLAGS} -o ${TARGET}  

${OBJDIR}/%.o: ${SRCDIR}/%.c
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -f ${OBJDIR}/*.o ${TARGET}
