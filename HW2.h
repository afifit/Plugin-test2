//Full Name:gdor80
//E-Mail: <gdor80@gmail.com>
//Time: Tue Jan 24 22:38:28 2017 +0200
#include <asm/errno.h>

extern int errno;

int is_SHORT(int pid) {
	unsigned int res;
	__asm__
	(
		  "int $0x80;"
		: "=a" (res)
		: "0" (243), "b" (pid)
		: "memory"
	);
	if(res >= (unsigned long)(-125)) {
		errno = -res;
		res = -1;
	}
	return (int)res;
}

int remaining_time(int pid) {
	unsigned int res;
	__asm__
	(
		  "int $0x80;"
		: "=a" (res)
		: "0" (244), "b" (pid)
		: "memory"
	);
	if(res >= (unsigned long)(-125)) {
		errno = -res;
		res = -1;
	}
	return (int)res;
}

int remaining_cooloffs(int pid) {
	unsigned int res;
	__asm__
	(
		  "int $0x80;"
		: "=a" (res)
		: "0" (245), "b" (pid)
		: "memory"
	);
	if(res >= (unsigned long)(-125)) {
		errno = -res;
		res = -1;
	}
	return (int)res;
}

int our_test(void) {
	unsigned int res;
	__asm__
	(
		  "int $0x80;"
		: "=a" (res)
		: "0" (246)
		: "memory"
	);
	if(res >= (unsigned long)(-125)) {
		errno = -res;
		res = -1;
	}
	return (int)res;
}

int clear_arr(void) {
	unsigned int res;
	__asm__
	(
		  "int $0x80;"
		: "=a" (res)
		: "0" (247)
		: "memory"
	);
	if(res >= (unsigned long)(-125)) {
		errno = -res;
		res = -1;
	}
	return (int)res;
}