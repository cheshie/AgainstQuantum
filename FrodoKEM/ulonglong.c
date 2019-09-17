#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

int main(int argc, char *argv[])
{
    printf("Size of int : %ld byte, Max value : %d, Min value : %d\n", sizeof(int), INT_MAX, INT_MIN);
    printf("Size of long : %ld byte, Max value : %d, Min value : %d\n", sizeof(long), LONG_MAX, LONG_MIN);
    printf("\n");
    printf("Size of unsigned int : %ld byte, Max value : %u, Min value : %d\n", sizeof(unsigned int), UINT_MAX, 0);
    printf("Size of unsigned long : %ld byte, Max value : %lu, Min value : %d\n", sizeof(unsigned long long), ULLONG_MAX, 0);
    
    long i = INT_MAX + 1;
    printf("\n\nOkay, testing. Max long: %i\n",i);
    unsigned long long j = INT_MAX + 1;
    printf("\n\nOkay, testing. Max unsigned long long: %i\n",j);
    return 0;
}
