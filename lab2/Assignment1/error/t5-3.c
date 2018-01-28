
void main()
{
	int a, b, c, d;
        int *p, *q, *r, *s

        *p=&a, *q=&b, *r=&c, *s=&d;
	*p = 3;		// '*p' - register v0
	*r = 4;		// '*r' - register v1
	*q = *p;	// '*q' - register v0
	*s = *r;	// '*s' - register v1
	*p = *s;	// '*p' - register v1
	*r = *q;	// '*r' - register v0
}
