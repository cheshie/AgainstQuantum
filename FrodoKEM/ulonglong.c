#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

int f(int *s)
{
	printf("s: ");
	for (int i=0; i<5; i++)
	{
		printf("%d, ",s[i]);
	}
	printf("\n\n");
	s+= 1;

	return 0;
}

int u1632()
{
	u_int16_t e[6] = {1,2,3,4,5,6};
	u_int16_t o[6];

	for (int i = 0; i < 6; i += 2) 
	{
		
        	*((u_int32_t*)&o[i]) = *((u_int32_t*)&e[i]);
        }	 
	

	printf("e: ");
	for(int i=0; i<6; i++)
		printf("%i",e[i]);
	printf("\n\n");
	
	printf("o: ");
	for(int i=0; i<6; i++)
		printf("%i",o[i]);
	printf("\n\n");
	
	
	return 0;
}

int frodo_mul_test()
{
	u_int8_t a[] = {1,2,3,4,5,6,7,8};
	u_int8_t b[] = {9,9,9,9,9,9,9,9};

	for (int i=0; i<8; i+=2)
		*((u_int16_t*)&a[i]) = *((u_int16_t*)&b[i]);
	
	printf("a: ");
	for(int i=0; i<8; i++)
		printf("%i",a[i]);
	printf("\nAfter change in a: \n\n");
	
	b[6] = 33;
	b[7] = 33;

	a[0] = 22;
	a[1] = 22;


	printf("a: ");
	for(int i=0; i<8; i++)
		printf("%i",a[i]);
	printf("\n");

	printf("b: ");
	for(int i=0; i<8; i++)
		printf("%i",b[i]);
	return 0;
}

int value_test()
{
	u_int16_t a = -1;
	u_int8_t  b = -1;

	printf("i => a: %i   b: %i\n",a,b);
	printf("u => a: %u   b: %u\n\n\n",a,b);

	u_int16_t w = 0;
       	u_int16_t mask = (1 << 8) - 1;
	int  nbits   = 8;
	unsigned char bits = 7;
	u_int8_t  n1   = w >> (bits-nbits);
	unsigned char t = (w >> (bits-nbits)) & mask;

	printf("(bits-nbits): %i\n",(bits-nbits));
	printf("mask: %i\n",mask);
	printf("w >> (...): %i\n",n1);
	printf("(...) & mask: %i\n",n1 & mask);
	printf("t: %i\n",t);


	return 1;
}



int main(int argc, char *argv[])
{
//	frodo_mul_test();
	int sk[3];

	for(int i =0; i<3; i++)
		printf("%i, ",sk[i]);
//value_test();



//    printf("Size of int : %ld byte, Max value : %d, Min value : %d\n", sizeof(int), INT_MAX, INT_MIN);
//    printf("Size of long : %ld byte, Max value : %d, Min value : %d\n", sizeof(long), LONG_MAX, LONG_MIN);
//    printf("\n");
//    printf("Size of unsigned int : %ld byte, Max value : %u, Min value : %d\n", sizeof(unsigned int), UINT_MAX, 0);
//    printf("Size of unsigned long : %ld byte, Max value : %lu, Min value : %d\n", sizeof(unsigned long long), ULLONG_MAX, 0);

    	
	//int tab[5] = {1,2,3,4,5};
	//int *p = tab;
	
	//printf("before: %i // %d\n\n",tab, tab[0]);
	//f(tab);
	//printf("after: %i // %d",tab, tab[0]);
	//for (int i=0; i < 5; i++)
	//{
	//	printf("tab[%i]= %i\n",i,p[0]);
	//	p += 1;
	//}

	//u1632();

	//u_int16_t ar[5] = {1,2,3,4,5};
        //u_int8_t  *tgr  = ar;
	
	//printf("ar: ");
	//for(int i=0; i<5; i++)
	//	printf("%i",ar[i]);
	//printf("\n\n");

	
	//printf("ar16: ");
	//for(int i=0; i<10; i++)
	//	printf("%i",tgr[i]);
	//printf("\n\n");
	exit(0);
}
		
	

