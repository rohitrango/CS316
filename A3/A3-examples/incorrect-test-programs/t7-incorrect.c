void main(){
	int l,t,a,m,n,b,u,v;
	int *pl,*pt,*pa,*pm,*pn,*pb,*pu,*pv;
	pl=&l;
	pt=&t;
	pa=&a;
	pm=&m;
	pn=&n;
	pb=&b;
	pu=&u;
	pv=&v;
	if(*pl){
		while(*pt<50){
			*pa=10;
		}
		*pb=10;
		while(*pt<100){
		*pm=30;
		}
		*pn=100;
	}
	*pu=300;
}
