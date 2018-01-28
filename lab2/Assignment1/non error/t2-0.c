void main()
{
	int a, b;
	int *p, *q;

	p = &a, q = &b;
	*p = 3;
	*q = *p;
}
