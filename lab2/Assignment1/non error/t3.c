void main()
{
	int a, b;
	int *p, *q;

         p = &a;
	*p = 3;
	*p = 9;
	*q = *p;
}
