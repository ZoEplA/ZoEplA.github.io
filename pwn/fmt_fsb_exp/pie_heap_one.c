#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <signal.h>

void echo() {
    int size = 0x200;
    char *buf = malloc(size);
    memset(buf, 0, size);

    fgets(buf, size, stdin);
    printf(buf);
    puts("\nain't it cool, bye now");
}

void timeout() {
    puts("Time is up");
    exit(1);
}

void welcome() {
    setvbuf(stdin, 0LL, 2, 0LL);
    setvbuf(stdout, 0LL, 2, 0LL);

    char welcome[] =
        "================================================\n"
        "Welcome to the super echo-mon-better system, it \n"
        "will echo anything you said, like:\n\n"
        "Melody: I wanna a flag, mom\n"
        "Mom: I wanna a flag, mom\n"
        "================================================\n";
    puts(welcome);

    signal(SIGALRM, timeout);
    alarm(5);
}

void echo_mon_better() {
    int i = 0;
    echo();
    return 0;
}

int main(int argc, char const *argv[]) {
    welcome();
    echo_mon_better();
    return 0;
}
