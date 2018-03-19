int a;
float b, *c, **d;


void foo() {
	a = b;
	aaa(a);
}


void main(int argc, int a, float c)
{
	int *a; 
	*a = 2;
	if(a < b) { 
		c = a;
		b = b;
	}
	foo(a, *b, &c);
}