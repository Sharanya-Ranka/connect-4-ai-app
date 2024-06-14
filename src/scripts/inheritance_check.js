class A {
  constructor(a) {
    this.a = a;
  }

  modifyA() {
    this.a += this.getModifier();
  }

  getModifier() {
    return 100;
  }
}

class AD extends A {
  //   modifyA() {
  //     this.a += 2;
  //   }

  getModifier() {
    return 200;
  }
}

ad_o = new AD(3);
ad_o.modifyA();
console.log(ad_o.a);
