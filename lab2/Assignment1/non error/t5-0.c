void main()
{
	int a, b, c, d;
	int *p, *q, *r, *s;
        
        p=&a, q=&b, r=&c, s=&d;
	*p = 3;
	*q = *p;
	*r = 2;
	*q = *r;
	*s = *r;
	*p = *q;
	*s = 5;
	*p = 10;
	*q = *s;
}
