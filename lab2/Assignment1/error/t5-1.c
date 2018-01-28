void main ()
{
	int a, b = 7;
	int c, d;
	int *p, *q, *r, *s; 

        p=&a, q=&b, r=&c, s=&d;
	*p = *q;
	*p = 3;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*p = 4;
	*r = 4;
	*q = *p;
}
