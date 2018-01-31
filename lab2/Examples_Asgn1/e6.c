void main() {
	// Comment a=M
	// a = &M;
 	// Non-working examples
	// p = *z= *y;
	// p = *z = 5;
	// a = *p = *q = 5;
	// *p = &a;
	// *p = a = b = &M;
	int **p;
	int q;
	*p = &q;

	// Working examples
	// a = b = p;
	// *p = *p;
	// a = b;
	// b = 3;
	// *c= *a;
}
