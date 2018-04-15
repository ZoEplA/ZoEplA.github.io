#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <signal.h>

void echo() {
    char buf[0x200];
    memset(buf, 0, sizeof(buf));

    fgets(buf, sizeof(buf), stdin);
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

int main(int argc, char const *argv[]) {
    welcome();
    echo();
    return 0;
}
